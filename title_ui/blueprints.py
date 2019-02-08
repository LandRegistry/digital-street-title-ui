# Import every blueprint file
from title_ui.views import general
from title_ui.views import index


def register_blueprints(app):
    """Adds all blueprint objects into the app."""
    app.register_blueprint(general.general)
    app.register_blueprint(index.index)

    # All done!
    app.logger.info("Blueprints registered")
