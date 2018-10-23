// form to JSON
$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

var hands = new Vue({
    el: '#hands',
    data: {
        players: [],
        dealer: []
    },
    methods: {
      set_players: function (data) {
          this.players = data;

      },
      set_dealer: function (data) {
          this.dealer = data;
      }
    },
    delimiters: ['[[', ']]']
});


$(document).ready(function () {
    var message_form = $("#message_form");
    var bet_input = $("#bet_input");
    var socket = io.connect('http://' + document.domain + ':' + location.port);
        socket.on('connect', function() {
            socket.emit('connected', {data: 'I\'m connected!'});
        });

    socket.on('new_message', function (data) {
        var chat = $("#chat_textarea");
        var text = '\n' + data + chat.val();
        chat.val(text);
    });

    message_form.on('submit', function (e) {
        e.preventDefault();
        var str = message_form.serializeObject();
        socket.emit('chat_message', str);
        $(".input").val("");
    });

    socket.on('players_info', function (data) {
        hands.set_players(data);
    });

    socket.on('dealer_info', function (data) {
        hands.set_dealer(data);
    });

    socket.on('betting', function (data) {
        $(".game_buttons").prop('disabled', true);
        if(data === $("#username").text()){
            $(".bet_btn").prop('disabled', false);
        }
        else {
            $(".bet_btn").prop('disabled', true);
        }
    });

    socket.on('player', function (data) {
        console.log(data);
        if(data.name === $("#username").text()){
            $(".game_buttons").prop('disabled', false);
            if(!data.can_double) { $("#double").prop('disabled', true) }
        }
        else {
            $(".game_buttons").prop('disabled', true);
        }
    });

    $("#double").on('click', function () {
        $(".game_buttons").prop('disabled', true);
        socket.emit('double');
    });

    $('#bet').on('click', function () {
        $(".bet_btn").prop('disabled', true);
        socket.emit('bet', bet_input.val());
        bet_input.val("");
    });

    $('#take').on('click', function () {
        $(".game_buttons").prop('disabled', true);
        socket.emit('take');
    });

    $('#next').on('click', function () {
        $(".game_buttons").prop('disabled', true);
        socket.emit('next');
    });
});
