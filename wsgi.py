from EDM import create_app

app = create_app(config='prod')

if __name__ == '__main__':
    print(app.url_map)
    app.run(host=app.config['HOST'], port=app.config['PORT'])
    # socketio.run(app, host=app.config['HOST'], allow_unsafe_werkzeug=True)
