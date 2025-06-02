def init_app(bot_app):
    from commands import admin, batch, files, user
    admin.app = batch.app = files.app = user.app = bot_app
