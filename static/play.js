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

    bet_input.ionRangeSlider({
        min: 1,
        max: 100,
        step: 1,
        value: 10,
    });

    $(".irs").addClass('is-hidden');

    var slider = bet_input.data('ionRangeSlider');

    var socket = io.connect('http://' + document.domain + ':' + location.port);
        socket.on('connect', function() {
            socket.emit('connected', {data: 'I\'m connected!'});
        });

    socket.on('check_connection', function() {
        socket.emit('check_connected', $("#username").text());
    });

    socket.on('new_message', function (data) {
        if (data.chat){
            var chat = $("#chat_textarea");
            var text = data.message + '\n' + chat.val();
            chat.val(text);
        }
        else {
            var game_ta = $("#game_textarea");
            var text = data.message + '\n' + game_ta.val();
            game_ta.val(text);
        }

    });

    // window.addEventListener("beforeunload", function (e) {
    //     socket.emit('leave');
    // });

    message_form.on('submit', function (e) {
        e.preventDefault();
        var str = message_form.serializeObject();
        socket.emit('chat_message', str);
        $("#message").val("");
    });

    socket.on('players_info', function (data) {
        hands.set_players(data);
    });

    socket.on('dealer_info', function (data) {
        hands.set_dealer(data);
    });

    socket.on('betting', function (data) {
        var name = $("#username").text();
        if (name in data){
            $(".bet_form").removeClass("is-hidden");
            $(".irs").removeClass("is-hidden");
            slider.update({
                max: data[name],
            });
            $("html").css('background-color', '#ffd59d');
        }
    });

    socket.on('player', function (data) {
        console.log(data);
        if(data.previous){
            $("#" + data.previous).removeClass('card_active');
        }
        $("#" + data.name).addClass('card_active');
        if(data.name === $("#username").text()){
            $(".game_buttons").removeClass("is-hidden");

            if(!data.can_double) { $("#double").prop('disabled', true) }
            else {$("#double").prop('disabled', false)}

            if(!data.can_split) { $("#split").prop('disabled', true) }
            else { $("#split").prop('disabled', false) }

            $("html").css('background-color', '#ffd59d');
        }
        else {
            $(".game_buttons").addClass("is-hidden");
            $("html").css('background-color', '#FFFFFF');
        }
    });

    $("#leave").on('click', function() {
        socket.emit('leave');
        window.location.replace("//blackjack.nikitko.ru");
    });

    $("#double").on('click', function () {
        $(".game_buttons").addClass("is-hidden");
        socket.emit('double');
    });

    $('#bet').on('click', function () {
        $(".bet_form").addClass("is-hidden");
        $(".irs").addClass("is-hidden");
        $("html").css('background-color', '#FFFFFF');
        socket.emit('bet', bet_input.val(), $("#username").text());
        bet_input.val("");
    });

    $('#take').on('click', function () {
        socket.emit('take');
    });

    $('#split').on('click', function () {
        socket.emit('split');
    });

    $('#next').on('click', function () {
        $(".game_buttons").addClass("is-hidden");
        socket.emit('next');
    });

    $('#chat_tab_button').on('click', function () {
        $(".tab").removeClass('is-active');
        $(".chat_tab").addClass('is-active');
        $("#game_textarea").addClass('is-hidden');
        $("#chat_textarea").removeClass('is-hidden');
    });

    $('#game_tab_button').on('click', function () {
        $(".tab").removeClass('is-active');
        $(".game_tab").addClass('is-active');
        $("#chat_textarea").addClass('is-hidden');
        $("#game_textarea").removeClass('is-hidden');
    });
});
