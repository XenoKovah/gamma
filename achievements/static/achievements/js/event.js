document.addEventListener('DOMContentLoaded', function(){
    let eventTitleEl = document.getElementById('id_title');
    let eventTypeEl = document.getElementById('id_event_type');
    let eventNames = JSON.parse(eventTypeEl.dataset.eventNames);
    if(eventNames && Object.keys(eventNames).length != 0){
        eventTitleEl.value = eventNames[eventTypeEl.value];
        eventTypeEl.addEventListener('change', function (){
                eventTitleEl.value = eventNames[this.value];
            }
        );
    }
    else{
        var eventTypeRow = document.getElementsByClassName('field-event_type')[0];
        eventTypeRow.insertAdjacentHTML('beforebegin', '<p class="errornote">There are no available events</p>');
        eventTypeRow.hidden = true;
        document.getElementsByClassName('field-title')[0].hidden = true;
        submits = document.querySelectorAll('input[type="submit"]');
        for (const s of submits) {
          s.disabled = true;
        }
    }
});
