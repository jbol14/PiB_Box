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
/*
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
*/

//Funktioniert so nicht, da Firebase nur auf änderungen im eigentlichen 
//Dokument achtet, nicht auf referenzierte

db.collection("/company").doc("yDOcLJggM9S9nUNt1SuQ")
	.collection("location").doc("yti5YJIX1Cnw0Pek79en")
	.onSnapshot({
		includeMetadataChanges: true
	}, function(doc){
			recievedData = doc.data();
			//console.log(recievedData.Services)
			console.log(recievedData.Services);
			//Nicht hier, aber so ähnlich
			//Funktioniert
			recievedData.Services.forEach(function(service){
				db.collection("/company").doc(service)
				.onSnapshot({
					includeMetadataChanges:false
					},function(doc){
						console.log(doc.data())
					})
			})
		}
);


//Alternativer Ansatz:
// Services an einem Standort sind (mehr oder weniger) statisch
// => für alle Services von Hand listener setzen
// nicht schön aber funktioniert 
/*
db.collection("/company").doc("yDOcLJggM9S9nUNt1SuQ/service/GEANbCXCkdk6T3ke2e0W")
	.onSnapshot({
		includeMetadataChanges:false
		}, function(doc){
			recievedData = doc.data();
			console.log(recievedData);
		}
);

db.collection("/company").doc("yDOcLJggM9S9nUNt1SuQ/service/hYdSuDsb6ptXEW4eqteH")
	.onSnapshot({
		includeMetadataChanges:false
		},function(doc){
			recievedData = doc.data();
			console.log(recievedData);
		}
);
*/
