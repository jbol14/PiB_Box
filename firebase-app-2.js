const firebase = require('firebase');
const net = require('net');
require('firebase/firestore');
const apiKey = require('./api');

//Konstanten
const SOCKETFILE = '/tmp/unix.sock';
const location = 'yti5YJIX1Cnw0Pek79en/';

//Firebase-App initialisieren
firebase.initializeApp({
		apiKey : apiKey.getKey(),
		projectId : 'raspi-python-test' 
	}
);

const db = firebase.firestore();

let datastructure = {}

// Alle Services, die auf der Location registriert sind als Array holen
let locationReference = db.collection('/company/yDOcLJggM9S9nUNt1SuQ/location');
let services = locationReference.doc(location).get()
	.then(function(doc){
		if(doc.exists){
			//Debug
			//console.log('Document Data: ',doc.data().Services.length)
			let services = doc.data().Services;
			//services.forEach(service => console.log(service));
			
			//Für jeden Service/Box die zugehörigen Reservierungen holen
			//und Listener darauf setzen
			 services.forEach((service)=>{
				//Listener für solche Reservierungen, deren serviceID einem Service an diesem Standort entspricht
				db.collection("reservation").where("serviceID","==",service)
					.onSnapshot({includeMetadataChanges: true},(doc) => {
						doc.docs.forEach((document) => {
							//Prüfen, ob die Reservierung gelöscht werden soll oder nicht
							//Leider notwendig, da Listener nicht triggern wenn ein Dokument gelöscht wird
							if(!document.data().flaggedForDeletion){
								datastructure[document.id] = document.data()
								console.log("DATA: ",datastructure,"\n\n")
							}else{
								delete datastructure[document.id]
								console.log(datastructure)
							}
							// Datenstruktur im Pythonskript über Sockets aktualisieren
						})
							
					});
			 });
			 
		}
		else{
			console.log('No such Document')
		}
	})
	.catch(function(error){
			console.log(error);
	});

