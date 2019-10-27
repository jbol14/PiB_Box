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
						// Wird immer aufgerufen wenn irgendetwas mit den Reservierungen passiert
						reservationCollection.docChanges().forEach((change)=>{
							// Prüfen, was passiert ist
							// von interesse sind eigentlich nur neue Dokumente
							if (change.type === 'added'){
								console.log('Neues Dokument', change.doc.id); // Test
								//Neuen Listener auf das Dokument setzen
								db.collection("reservation").doc(change.doc.id)
									.onSnapshot({includeMetadataChanges:true},(reservation)=>{
										if(validReservation(reservation.data())){
											console.log('Gültige Reservierung',reservation.id,reservation.data()); //Test
											addReservation(reservation.id,reservation.data());
										}
										else{
											console.log('Reservierung abgelaufen',reservation.id); //Test
											deleteReservation(reservation.id);
										}
									});
							}
							//Unnötig
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
// Verhalten: Ergänzt die Nutzdaten der Reservierung um ID und den Typ (= ADD) der Aktion am Server und schreibt Daten in Socket
function addReservation(reservationId, reservation){
	payload = {
		id : reservationId,
		type : "ADD",
		payload : reservation
	}
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
