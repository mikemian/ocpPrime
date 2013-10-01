/**
 * Module dependencies.
 */

var express = require('express')
  , http = require('http')
  , execSync = require('exec-sync')
  , fs = require('fs');

var app = express();

// all environments
app.set('port', process.env.PORT || 42280);
app.use(express.logger('dev'));
app.use(express.bodyParser());
app.use(express.methodOverride());
app.use(app.router);

// development only
if ('development' == app.get('env')) {
  app.use(express.errorHandler());
}

app.get('/getBIOS', 
	function(req, res){ 
		var bios = fs.readFileSync('/dev/nvram', 'binary');
		res.setHeader('Content-Length', bios.length);
		res.end(bios, 'binary');
	}
);

app.post('/setBIOS', 
	function(req, res) {
		fs.rename(req.files.BIOS.path, '/dev/nvram');
		res.send('BIOS Updated');
	}
);


app.get('/nodeInfo',
	function(req, res){
		var nodeInfo = sh.exec(__dirname + '/metrics/nodeInfo.py');
		res.json(nodeInfo);
	}
);

http.createServer(app).listen(app.get('port'), function(){
  console.log('ocp-agent listening on port ' + app.get('port'));
});
