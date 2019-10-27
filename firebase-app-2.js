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
					.onSnapshot({includeMetadataChanges: true},(reservationCollection) => {
						reservationCollection.docChanges().forEach((change)=>{
							if (change.type === 'added'){
								console.log('Neues Dokument', change.doc.id);
								//Neuen Listener auf das Dokument setzen
								db.collection("reservation").doc(change.doc.id)
									.onSnapshot({includeMetadataChanges:true},(reservation)=>{
										//console.log('Reservierung verändert!\n',reservation.data())
										// TODO: Prüfen ob Reservierunge gültig is
										//  D.h. resTill liegt nicht in der Vergangenheit
										if(validReservation(reservation.data())){
											console.log('Gültige Reservierung',reservation.id,reservation.data());
											addReservation(reservation.id,reservation.data());
										}
										else{
											console.log('Reservierung abgelaufen',reservation.id);
											deleteReservation(reservation.id);
										}
										

										// TODO: Änderungen an Server weiterreichen über Unix Socket

									});
							}
							else{
								console.log(change.type);
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
	if(!reservation.companyHasDeleted && !reservation.userHasDeleted && timeNow < reservation.resTill){
		return true;
	}
	else{
		return false;
	}
}

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

function addReservation(reservationId, reservation){
	console.log(reservation);
	reservation.id = reservationId;
	reservation.type = "ADD";
	//console.log(reservation);
	updateBoxServer(reservation);
}

function deleteReservation(reservationId){
	reservation = {
		id:reservationId,
		type: "DELETE"
	};
	console.log(reservation);
	updateBoxServer(reservation);
}
