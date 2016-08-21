var DHT = require('bittorrent-dht')
var magnet = require('magnet-uri')

var uri = 'magnet:?xt=urn:btih:ce582dc72b5a61c14784cbcefb611fca433267cd'
var parsed = magnet(uri)

console.log(parsed.infoHash)

var dht = new DHT()

dht.listen(20000, function () {
  console.log('now listening')
})
dht.on('announce',(peer,infohash)=>{
  console.log("收到声明请求:"+infohash);
})
dht.on('node',(node)=>{
  console.log("新节点:"+node+new Date());
})
// find peers for the given torrent info hash
//dht.lookup(parsed.infoHash)
dht.on('peer', function (peer, infoHash, from) {
  console.log('found potential peer ' + peer.host + ':' + peer.port + ' through ' + from.host + ':' + from.port)
})
