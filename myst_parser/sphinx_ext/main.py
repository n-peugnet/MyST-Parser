"""The setup for the sphinx extension."""
from typing import Any

from sphinx.application import Sphinx

from myst_parser.transforms.local_links import MdDocumentLinks


def setup_sphinx(app: Sphinx, load_parser=False):
    """Initialize all settings and transforms in Sphinx."""
    # we do this separately to setup,
    # so that it can be called by external packages like myst_nb
    from myst_parser.config.main import MdParserConfig
    from myst_parser.parsers.sphinx_ import MystParser
    from myst_parser.sphinx_ext.directives import (
        FigureMarkdown,
        SubstitutionReferenceRole,
    )
    from myst_parser.sphinx_ext.mathjax import override_mathjax
    from myst_parser.sphinx_ext.myst_refs import MystRefrenceResolver, ObjectsBuilder

    if load_parser:
        app.add_source_suffix(".md", "markdown")
        app.add_source_parser(MystParser)

    app.add_role("sub-ref", SubstitutionReferenceRole())
    app.add_directive("figure-md", FigureMarkdown)

    app.add_transform(MdDocumentLinks)
    app.add_post_transform(MystRefrenceResolver)
    app.add_builder(ObjectsBuilder)

    for name, default, field in MdParserConfig().as_triple():
        if not field.metadata.get("docutils_only", False):
            # TODO add types?
            app.add_config_value(f"myst_{name}", default, "env", types=Any)

    app.connect("builder-inited", create_myst_config)
    app.connect("builder-inited", override_mathjax)


def create_myst_config(app):
    from sphinx.util import logging

    # Ignore type checkers because the attribute is dynamically assigned
    from sphinx.util.console import bold  # type: ignore[attr-defined]

    from myst_parser import __version__
    from myst_parser.config.main import MdParserConfig

    logger = logging.getLogger(__name__)

    values = {
        name: app.config[f"myst_{name}"]
        for name, _, field in MdParserConfig().as_triple()
        if not field.metadata.get("docutils_only", False)
    }

    try:
        app.env.myst_config = MdParserConfig(**values)
        logger.info(bold("myst v%s:") + " %s", __version__, app.env.myst_config)
    except (TypeError, ValueError) as error:
        logger.error("myst configuration invalid: %s", error.args[0])
        app.env.myst_config = MdParserConfig()
