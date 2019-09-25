const firebase = require('firebase');
const net = require('net');
require('firebase/firestore');
// Helper that contains API Key
const apiKey = require("./api")
// Path of Socketfile
const SOCKETFILE = '/tmp/unix.sock';

function updateDataStructure(boxData){
	const client = net.createConnection({path: SOCKETFILE});
	client.on('connect', ()=>{
		console.log('Connected to Socket');
		client.write(JSON.stringify(boxData));
	}); 
	client.on('data', (data)=>{
		console.log(data.toString());
	});
	client.on('end', ()=>{
		console.log('Disconnected from Socket');
	});
	client.on('error', (err)=>{
		console.error(err);
	});
}

firebase.initializeApp({
	apiKey : apiKey.getKey(),
	projectId : 'raspi-python-test'
});

const db = firebase.firestore();

db.collection('/Standort').doc('CLZ2/')
	.onSnapshot({
	 includeMetadataChanges : false		
	}, function(doc){
		recievedData = doc.data();
		console.log(recievedData);
		recievedData.type = 'UPDATE';
		updateDataStructure(recievedData);
	}
);
