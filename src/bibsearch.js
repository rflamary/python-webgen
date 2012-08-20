

<!--
// QuickSearch script for JabRef HTML export 
// Version: 2.0
//
// Copyright (c) 2006-2008, Mark Schenk
//
// This software is distributed under a Creative Commons Attribution 3.0 License
// http://creativecommons.org/licenses/by/3.0/
 
// Some features:
// + optionally searches Abstracts and Reviews
// + allows RegExp searches
//   e.g. to search for entries between 1980 and 1989, type:  198[0-9]
//   e.g. for any entry ending with 'symmetry', type:  symmetry$
//   e.g. for all reftypes that are books: ^book$, or ^article$
//   e.g. for entries by either John or Doe, type john|doe
// + easy toggling of Abstract/Review/BibTeX
 
// Search settings
var searchAbstract = true;
var searchReview = true;
 
// Speed optimisation introduced some esoteric problems with certain RegExp searches
// e.g. if the previous search is 200[-7] and the next search is 200[4-7] then the search doesn't work properly until the next 'keyup'
// hence the searchOpt can be turned off for RegExp adepts
var searchOpt = true;
 
if (window.addEventListener) {
	window.addEventListener("load",initSearch,false); }
else if (window.attachEvent) {
	window.attachEvent("onload", initSearch); }
 
function initSearch() {
	// basic object detection
	if(!document.getElementById || !document.getElementsByTagName) { return; }
	if (!document.getElementById('qstable')||!document.getElementById('qs')) { return; }
 
	// find QS table and appropriate rows
	searchTable = document.getElementById('qstable');
	var allRows = searchTable.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
 
	// split all rows into entryRows and infoRows (e.g. abstract, review, bibtex)
	entryRows = new Array();
	infoRows = new Array(); absRows = new Array(); revRows = new Array();
 
	for (var i=0, k=0, j=0; i<allRows.length;i++) {
		if (allRows[i].className.match(/entry/)) {
			entryRows[j++] = allRows[i];
		} else {
			infoRows[k++] = allRows[i];
			// check for abstract/review
			if (allRows[i].className.match(/abstract/)) {
				absRows.push(allRows[i]);
			} else if (allRows[i].className.match(/review/)) {
				revRows.push(allRows[i]);
			}
		}
	}
 
	//number of entries and rows
	numRows = allRows.length;
	numEntries = entryRows.length;
	numInfo = infoRows.length;
	numAbs = absRows.length;
	numRev = revRows.length;
 
	//find the query field
	qsfield = document.getElementById('qsfield');
 
	// previous search term; used for speed optimisation
	prevSearch = '';
 
	//find statistics location
	stats = document.getElementById('stat');
	setStatistics(-1);
 
	// creates the appropriate search settings
	createQSettingsDialog();
 
	// shows the searchfield
	document.getElementById('qs').style.display = 'block';
	document.getElementById('qsfield').onkeyup = testEvent;
}
 
function quickSearch(tInput){
 
	 if (tInput.value.length == 0) {
		showAll();
		setStatistics(-1);
		qsfield.className = '';
		return;
	} else {
		// only search for valid RegExp
		try {
			var searchText = new RegExp(tInput.value,"i")
			closeAllInfo();
			qsfield.className = '';
		}
		catch(err) {
			prevSearch = tInput.value;
			qsfield.className = 'invalidsearch';
			return;
		}
	}
	
	// count number of hits
	var hits = 0;
 
	// start looping through all entry rows
	for (var i = 0; cRow = entryRows[i]; i++){
 
		// only show search the cells if it isn't already hidden OR if the search term is getting shorter, then search all
		// some further optimisation is possible: if the search string is getting shorter, and the row is already visible, skip it. Then be careful with hits!
		if(!searchOpt || cRow.className.indexOf('noshow')==-1 || tInput.value.length <= prevSearch.length){
			var found = false; 
 
			var inCells = cRow.getElementsByTagName('td');
			var numCols = inCells.length;
				
			for (var j=0; j<numCols; j++) {
				cCell = inCells[j];
				var t = cCell.innerText?cCell.innerText:getTextContent(cCell);
				if (t.search(searchText) != -1){ 
					found=true; 
					break;
				} 
			}
 
			// look for further hits in Abstract and Review
			if(!found) {
				var articleid = cRow.id;
				if(searchAbstract && (abs = document.getElementById('abs_'+articleid))) {
					if (getTextContent(abs).search(searchText) != -1){ found=true; } 
				}
				if(searchReview && (rev = document.getElementById('rev_'+articleid))) {
					if (getTextContent(rev).search(searchText) != -1){ found=true; } 
				}
			}
			
			if(found) {
				cRow.className = 'entry show';
				hits++;
			} else {
				cRow.className = 'entry noshow';
			}
		}
	}
 
	// update statistics
	setStatistics(hits)
	
	// set previous search value
	prevSearch = tInput.value;
}
 
function toggleInfo(articleid,info) {
 
	var entry = document.getElementById(articleid);
	var abs = document.getElementById('abs_'+articleid);
	var rev = document.getElementById('rev_'+articleid);
	var bib = document.getElementById('bib_'+articleid);
	
	if (abs && info == 'abstract') {
		if(abs.className.indexOf('abstract') != -1) {
		abs.className.indexOf('noshow') == -1?abs.className = 'abstract noshow':abs.className = 'abstract';
		}
	} else if (rev && info == 'review') {
		if(rev.className.indexOf('review') != -1) {
		rev.className.indexOf('noshow') == -1?rev.className = 'review noshow':rev.className = 'review';
		}
	} else if (bib && info == 'bibtex') {
		if(bib.className.indexOf('bibtex') != -1) {
		bib.className.indexOf('noshow') == -1?bib.className = 'bibtex noshow':bib.className = 'bibtex';
		}		
	} else { 
		return;
	}
 
	// check if one or the other is available
	var revshow = false;
	var absshow = false;
	var bibshow = false;
	(abs && abs.className.indexOf('noshow') == -1)? absshow = true: absshow = false;
	(rev && rev.className.indexOf('noshow') == -1)? revshow = true: revshow = false;	
	(bib && bib.className == 'bibtex')? bibshow = true: bibshow = false;
	
	// highlight original entry
	if(entry) {
		if (revshow || absshow || bibshow) {
		entry.className = 'entry highlight show';
		} else {
		entry.className = 'entry show';
		}		
	}
	
	// When there's a combination of abstract/review/bibtex showing, need to add class for correct styling
	if(absshow) {
		(revshow||bibshow)?abs.className = 'abstract nextshow':abs.className = 'abstract';
	} 
	if (revshow) {
		bibshow?rev.className = 'review nextshow': rev.className = 'review';
	}
	
}
 
function setStatistics (hits) {
	if(hits < 0) { hits=numEntries; }
	if(stats) { stats.firstChild.data = hits + '/' + numEntries}
}
 
function getTextContent(node) {
	// Function written by Arve Bersvendsen
	// http://www.virtuelvis.com
	
	if (node.nodeType == 3) {
	return node.nodeValue;
	} // text node
	if (node.nodeType == 1) { // element node
	var text = [];
	for (var chld = node.firstChild;chld;chld=chld.nextSibling) {
		text.push(getTextContent(chld));
	}
	return text.join("");
	} return ""; // some other node, won't contain text nodes.
}
 
function showAll(){
	// first close all abstracts, reviews, etc.
	closeAllInfo();
 
	for (var i = 0; i < numEntries; i++){
		entryRows[i].className = 'entry show'; 
	}
}
 
function closeAllInfo(){
	for (var i=0; i < numInfo; i++){
		if (infoRows[i].className.indexOf('noshow') ==-1) {
			infoRows[i].className = infoRows[i].className + ' noshow';
		}
	}
}
 
function testEvent(e){
	if (!e) var e = window.event;
	quickSearch(this);
}
 
function clearQS() {
	qsfield.value = '';
	quickSearch(qsfield);
}
 
function redoQS(){
	showAll();
	quickSearch(qsfield);
}
 
// Create Search Settings
 
function toggleQSettingsDialog() {
 
	var qssettings = document.getElementById('qssettings');
	
	if(qssettings.className.indexOf('active')==-1) {
		qssettings.className = 'active';
 
		if(absCheckBox && searchAbstract == true) { absCheckBox.checked = 'checked'; }
		if(revCheckBox && searchReview == true) { revCheckBox.checked = 'checked'; }
 
	} else {
		qssettings.className= '';
	}
}
 
function createQSettingsDialog(){
	var qssettingslist = document.getElementById('qssettings').getElementsByTagName('ul')[0];
	
	if(numAbs!=0) {
		var x = document.createElement('input');
		x.id = "searchAbs";
		x.type = "checkbox";
		x.onclick = toggleQSetting;
		var y = qssettingslist.appendChild(document.createElement('li')).appendChild(document.createElement('label'));
		y.appendChild(x);
		y.appendChild(document.createTextNode('search abstracts'));		
	}
	if(numRev!=0) {
		var x = document.createElement('input');
		x.id = "searchRev";
		x.type = "checkbox";		
		x.onclick = toggleQSetting;
		var y = qssettingslist.appendChild(document.createElement('li')).appendChild(document.createElement('label'));		
		y.appendChild(x);		
		y.appendChild(document.createTextNode('search reviews'));
	}
		
	// global variables
	absCheckBox = document.getElementById('searchAbs');
	revCheckBox = document.getElementById('searchRev');
	
	// show search settings
	if(absCheckBox||revCheckBox) {
		document.getElementById('qssettings').style.display = 'none';
	}
}
 
function toggleQSetting() {
	if(this.id=='searchAbs') { searchAbstract = !searchAbstract; }
	if(this.id=='searchRev') { searchReview = !searchReview; }
	redoQS()
} 
 
-->
