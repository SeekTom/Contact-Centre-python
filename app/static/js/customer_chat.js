$(function() {
    // Get handle to the chat div 
    var $chatWindow = $('#messages');

    // Our interface to the Chat service
    var chatClient;

    // A handle to the "general" chat channel - the one and only channel we
    // will have in this sample app
    var generalChannel;

    // The server will assign the client a random username - store that value
    // here
    var username;

    function getRandomArbitrary(min, max) {
        return Math.random() * (max - min) + min;
    }
    // Helper function to print info messages to the chat window
    function print(infoMessage, asHtml) {
        var $msg = $('<div class="info">');
        if (asHtml) {
            $msg.html(infoMessage);
        } else {
            $msg.text(infoMessage);
        }
        $chatWindow.append($msg);
    }

    // Helper function to print chat message to the chat window
    function printMessage(fromUser, message) {
        var $user = $('<span class="username">').text(fromUser + ':');
        if (fromUser === username) {
            $user.addClass('me');
        }
        var $message = $('<span class="message">').text(message);
        var $container = $('<div class="message-container">');
        $container.append($user).append($message);
        $chatWindow.append($container);
        $chatWindow.scrollTop($chatWindow[0].scrollHeight);
    }

    // Alert the user they have been assigned a random username
    print('Logging in...');

    // Get an access token for the current user, passing a username (identity)
    // and a device ID - for browser-based apps, we'll always just use the 
    // value "browser"
    $.getJSON('/token', {
        identity: 'customer',
        device: 'browser'
    }, function(data) {
        // Alert the user they have been assigned a random username
        username = 'customer'
        //print('You have been assigned a random username of: '
          //  + '<span class="me">' + username + '</span>', true);

        // Initialize the Chat client
        chatClient = new Twilio.Chat.Client(data.token);
        chatClient.getSubscribedChannels().then(createOrJoinGeneralChannel);

    });


    function createOrJoinGeneralChannel() {
         //     $.get( "/createChatTask/", function( data ) {
           // alert( "Data Loaded: " + data.TaskSid );
            //var taskSid =  data.TaskSid
           var channelName = getRandomArbitrary(0,10000000);
           print('Attempting to join ' + channelName + ' chat channel...');
                var promise = chatClient.getChannelByUniqueName(channelName);
                promise.then(function(channel) {
                    generalChannel = channel;
                    console.log('Found ' + channel.friendlyName + ' channel:');
                    console.log(generalChannel);

                    setupChannel();
                }).catch(function() {
                    // If it doesn't exist, let's create it
                    console.log('Creating general channel');
                    chatClient.createChannel({
                        uniqueName: channelName,
                        friendlyName: 'Customer request ' + channelName,
                    }).then(function(channel) {
                        console.log('Created +' + channelName + +' channel:');
                        console.log(channel);
                        generalChannel = channel;
                        setupChannel();


                    });
                });

           // });

    }

    // Set up channel after it has been found
    function setupChannel() {
        // Join the general channel

        generalChannel.join().then(function(channel) {
            print('Joined channel as '
                + '<span class="me">Welcome ' + username + ', please wait for an agent to join you.</span>.', true);
              $.post("/createChatTask/", {
                channel: channel.sid,
            });

        });



        // Listen for new messages sent to the channel
        generalChannel.on('messageAdded', function(message) {
            printMessage(message.author, message.body);
        });
    }

    // Send a new message to the general channel
    var $input = $('#chat-input');
    $input.on('keydown', function(e) {
        if (e.keyCode == 13 && generalChannel) {
            generalChannel.sendMessage($input.val())
            $input.val('');
        }
    });
});