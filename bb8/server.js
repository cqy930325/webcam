// modules
var childProcess = require('child_process'), ws = require('ws'), http = require('http');

// configuration files
var configServer = require('./lib/config/server');

/// Video streaming section
// Reference: https://github.com/phoboslab/jsmpeg/blob/master/stream-server.js

var STREAM_MAGIC_BYTES = 'jsmp'; // Must be 4 bytes
var width = 640;
var height = 480;

// WebSocket server
var wsServer = new (ws.Server)({ port: configServer.wsPort });
console.log('WebSocket server listening on port ' + configServer.wsPort);

wsServer.on('connection', function(socket) {
  // Send magic bytes and video size to the newly connected socket
  // struct { char magic[4]; unsigned short width, height;}
  var streamHeader = new Buffer(8);

  streamHeader.write(STREAM_MAGIC_BYTES);
  streamHeader.writeUInt16BE(width, 4);
  streamHeader.writeUInt16BE(height, 6);
  socket.send(streamHeader, { binary: true });

  console.log('New WebSocket Connection (' + wsServer.clients.length + ' total)');

  socket.on('close', function(code, message){
    console.log('Disconnected WebSocket (' + wsServer.clients.length + ' total)');
  });
});

wsServer.broadcast = function(data, opts) {
  for(var i in this.clients) {
    if(this.clients[i].readyState == 1) {
      this.clients[i].send(data, opts);
    }
    else {
      console.log('Error: Client (' + i + ') not connected.');
    }
  }
};

// HTTP server to accept incoming MPEG1 stream
http.createServer(function (req, res) {
  console.log(
    'Stream Connected: ' + req.socket.remoteAddress +
    ':' + req.socket.remotePort + ' size: ' + width + 'x' + height
  );

  req.on('data', function (data) {
    wsServer.broadcast(data, { binary: true });
  });
}).listen(configServer.streamPort, function () {
  console.log('Listening for video stream on port ' + configServer.streamPort);

  // Run do_ffmpeg.sh from node                                                   
  childProcess.exec('bash do_ffmpeg.sh');
});