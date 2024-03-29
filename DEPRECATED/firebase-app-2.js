const firebase = require('firebase');
const net = require('net');
require('firebase/firestore');
const apiKey = require('../Firebase/api');

//Konstanten
const SOCKETFILE = '/tmp/unix.sock';
const location = 'yti5YJIX1Cnw0Pek79en/';

//Firebase-App initialisieren
firebase.initializeApp({
    apiKey: apiKey.getKey(),
    authDomain: "boxsystem-a20f5.firebaseapp.com",
    databaseURL: "https://boxsystem-a20f5.firebaseio.com",
    projectId: "boxsystem-a20f5",
    storageBucket: "boxsystem-a20f5.appspot.com",
    messagingSenderId: "43374441475",
    appId: "1:43374441475:web:1a57abdbdd3ad823fc8a36",
    measurementId: "G-YL4Q3QH12C"
  }
);

const db = firebase.firestore();

// Alle Services, die auf der Location registriert sind als Array holen
let locationReference = db.collection('/company/yDOcLJggM9S9nUNt1SuQ/location');
let services = locationReference.doc(location).get();

services.then(function(doc){
	if(doc.exists){
		
		let services = doc.data().Services;
			
		//Für jeden Service/Box die zugehörigen Reservierungen holen
		//und Listener darauf setzen
		services.forEach((service)=>{

			//Listener für Service setzen
			db.collection('/company/yDOcLJggM9S9nUNt1SuQ/service').doc(service)
			.onSnapshot({includeMetadataChanges:true}, (box)=> {
				console.log("This is a box",box.id,box.data());
				addService(box.id, box.data());
			});
				
			//Listener für solche Reservierungen, deren serviceID einem Service an diesem Standort entspricht
			db.collection("reservation").where("serviceID","==",service)
			.onSnapshot({includeMetadataChanges: true},(reservationCollection) => {
						
				// Wird immer aufgerufen wenn irgendetwas mit den Reservierungen passiert
				reservationCollection.docChanges().forEach((change)=>{
					// Prüfen, was passiert ist
					// von interesse sind eigentlich nur neue Dokumente
					if (change.type === 'added'){
						console.log('Neues Dokument', change.doc.id); // Test
								
						//Neuen Listener auf das Dokument setzen
						db.collection("reservation").doc(change.doc.id)
						.onSnapshot({includeMetadataChanges:false},(reservation)=>{
							reducedData = reservation.data();
							delete reducedData.used
							console.log("data: ",reducedData); //Test
							if(reservation.data() && validReservation(reservation.data())){
										
								//Listener für Shares setzen
								db.collection('sharing').where('reservationID','==', reservation.id)
								.onSnapshot({includeMetadataChanges : true}, (shares)=>{
									shares.docChanges().forEach((change)=>{
										if(change.type === 'added'){
											addShare(change.doc.id, change.doc.data())
										}
									});
								});


								console.log('Gültige Reservierung',reservation.id,reducedData); //Test
								addReservation(reservation.id,reducedData);
							}
							else{
								console.log('Reservierung abgelaufen',reservation.id); //Test
								deleteReservation(reservation.id);
							}
						});
					}
					//Unnötig
					else{
						console.log("change type: ", change.type);
					}
				});
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

//Input: Eine Reservierung
//Output: True, falls nicht zur LÃ¶schung geflaggt oder Mietzeitraum in der Vergangenheit liegt
//		  False, falls von user oder company zu gelÃ¶scht oder Mietzeitraum in Vergangenheit liegt
function validReservation(reservation){
	timeNow = firebase.firestore.Timestamp.now();
	console.log(timeNow.toMillis(), reservation.resTill.toMillis())
	if(!reservation.companyHasDeleted && !reservation.userHasDeleted && timeNow < reservation.resTill){
		return true;
	}
	else{
		return false;
	}
}

// Input: Ein Reservierungsdokument aus Firebase
// Output: void
// Verhalten: Stellt Verbindung zum Unix-Socker her und schreibt das Dokument
function updateBoxServer(document){
	const client = net.createConnection({path: SOCKETFILE});
	client.on('connect', ()=>{
		console.log('Connected to Socket');
		console.log(document.id)
		client.end(JSON.stringify(document));
	});
	client.on('data', (data)=>{
		console.log(data.toString());
	});
	client.on('end',()=>{
		console.log('Disconnected from Socket');
	});
	client.on('error',(error)=>{
		console.error(error,document);
	});
}

// Input: param1: ID einer Reservierung, param2: die Nutzdaten der Reservierung
// Output: void
// Verhalten: Ergänzt die Nutzdaten der Reservierung um ID und den Typ (= ADD_RESERVATION) der Aktion am Server und schreibt Daten in Socket
function addReservation(reservationId, reservation){
	reservation.resFrom = reservation.resFrom.toMillis(); //Neu, in Millisekunden umwandeln
	reservation.resTill = reservation.resTill.toMillis(); //Neu, in Millisekunden umwandeln
	payload = {
		id : reservationId,
		type : "ADD_RESERVATION",
		payload : reservation
	}
	updateBoxServer(payload);
}

// Input: shareId: ID eines shares, shareData: Daten des shares
//Output: void
//Verhalten: Ergänzt Nutzdaten eines Shares um dessen ID und den Typ (=ADD_SHARE) der Aktion am Server und schreibt Daten in Socket
function addShare(shareId, shareData){
	payload = {
		id : shareId,
		type : "ADD_SHARE",
		payload : shareData
	}
	console.log(payload) //Test
	updateBoxServer(payload)
}

function addService(serviceId, service){
	payload = {
		id : serviceId,
		type : "ADD_SERVICE",
		payload : service
	}
	console.log(payload); // Test
	updateBoxServer(payload);
}

// Input: param1 ID der zu löschenden Reservierung
// Output: void
// Verhalten: Erstellt ein Objekt bestehend aus ID der zu löschendne Reservierung und dem Typ (= DELETE) der Aktion am Server und schreibt in Socket
function deleteReservation(reservationId){
	payload = {
		id:reservationId,
		type: "DELETE"
	};
	console.log(payload); //Test
	updateBoxServer(payload);
}