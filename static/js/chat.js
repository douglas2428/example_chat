 $(function() {
      var conn = null;
      var userName = null;
      var target = null;

      function send(msg){
        if(conn==null)
          return false;
        conn.send(JSON.stringify(msg));
      }

      function log(msg) {
        var control = $('#chat_screen');
        control.html(control.html() + msg + '<br/>');
        control.scrollTop(control.scrollTop() + 1000);
      }

      /*---------------authenticate-------------------*/
      function check(data) {
        if(data.isAvailable == false) {
          userName = prompt('El usuario "'+data.username+'" ya fue seleccionado(o la cagaste al ingresar lat/lon). Ingrese otro');
          authenticate();
        }
      }
    
      function authenticate() {
        while(userName == null|| userName=='') {
          userName = prompt('Inserta nombre de usuario');
        }

        var lat = prompt("Ingrese una latitud (valida por favor, da ladilla validar eso)");
        var lon = prompt("Ingrese una longitud (valida por favor, da ladilla validar eso)");

        send({"data_type":"auth","data":{'username':userName,'lat':lat, 'lon':lon}})
      }
      /*---------------/authenticate-------------------*/

      function connect() {
        disconnect();

        var transports = $('#protocols input:checked').map(function(){
            return $(this).attr('id');
        }).get();

        conn = new SockJS('http://' + window.location.host + '/chat', transports);

        log('Connecting...');

        conn.onopen = function() {
          authenticate();
          log('Connected.');
          update_ui();
        };

        conn.onmessage = function(e) {
          msg = $.parseJSON(e.data);
          data=msg['data'];
          data_type=msg['data_type'];

          $("#title").html("Chat! room: '" + data.room + "'");

          if(data_type=="send_text") {
            if(msg['private'])
              log(data.username+'(privado): '+data.text);
            else
              log(data.username+': '+data.text);
          }
          else if(data_type=='send_list_users')
          {
            $("#users_list").html("");
            data.forEach(function(username) {
              $("#users_list").append("<p class='user-connected' target='" + username + "'>" + username + "</p>");
            });
          }
          else if(data_type=="auth"){

            if(!('error' in data))
                check(data); 
          }
            
        };

        conn.onclose = function() {
          log('Disconnected.');
          conn = null;
          update_ui();
        };
      }

      function disconnect() {
        if (conn != null) {
          log('Disconnecting...');

          conn.close();
          conn = null;

          update_ui();
        }
      }

      function update_ui() {
        var msg = '';

        if (conn == null || conn.readyState != SockJS.OPEN) {
          $('#status').text('disconnected');
          $('#connect').text('Connect');
        } else {
          $('#status').text('connected (' + conn.protocol + ')');
          $('#connect').text('Disconnect');
        }
      }

      $('#connect').click(function() {
        if (conn == null) {
          connect();
        } else {
          disconnect();
        }

        update_ui();
        return false;
      });

      $('#change_location').click(function() {
        var lat = prompt("Ingrese una latitud (valida por favor, da ladilla validar eso)");
        var lon = prompt("Ingrese una longitud (valida por favor, da ladilla validar eso)");
        send({'data_type':'change_location', 'lat':lat, 'lon':lon});
      });

      $(document).on('click','p.user-connected',function() {
        target = $(this).attr('target');

        console.log(target);
        
        if(target != null)
          $("#user-target").html(target);
        else
          $("#user-target").html("Todos");
      });

      $('form').submit(function() {
        var text = $.encoder.encodeForHTML($("#message").val());
        if(text=="")
          return false;
        
        if(target != null)
          send({'data_type':'send_text', 'data':text, 'target':target});
        else
          send({'data_type':'send_text', 'data':text});

        $('#message').val('').focus();
        return false;
      });
    });