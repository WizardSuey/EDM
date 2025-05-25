from EDM import create_app, socketio

app = create_app(config='prod')

if __name__ == '__main__':
    print(app.url_map)
    # socketio.run(app, host=app.config['HOST'], port=app.config['PORT'])
    socketio.run(app, host=app.config['HOST'])
