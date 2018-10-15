var socket = io.connect('http://' + document.domain + ':' + location.port);
        socket.on('connect', function() {
            socket.emit('my event', {data: 'I\'m connected!'});
        });

$("#message_form").on('submit', function (e) {
    e.preventDefault();
    var str = JSON.stringify( $(form).serializeArray());
    console.log(str);
    socket.emit('chat_message', str);
});