 $(function() {
      var conn = null;
      var userName = null;

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
          userName = prompt('El usuario "'+data.username+'" ya fue seleccionado. Ingrese otro');
          authenticate();
        }
      }
    
      function authenticate() {
        while(userName == null|| userName=='') {
          userName = prompt('Inserta nombre de usuario');
        }
        send({"data_type":"auth","data":{'username':userName}})
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

          if(data_type=="send_text")
            log(data.username+': '+data.text);
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

      $('form').submit(function() {
        var text = $.encoder.encodeForHTML($("#message").val());
        if(text=="")
          return false;
        
        send({'data_type':'send_text',
             'data':text});
        
        $('#message').val('').focus();
        return false;
      });
    });