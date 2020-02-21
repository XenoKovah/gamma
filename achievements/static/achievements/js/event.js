document.addEventListener('DOMContentLoaded', function(){
    let eventTitleEl = document.getElementById('id_title');
    let eventTypeEl = document.getElementById('id_event_type');
    let eventNames = JSON.parse(eventTypeEl.dataset.eventNames);
    eventTitleEl.value = eventNames[eventTypeEl.value];
    eventTypeEl.addEventListener('change', function (){
            eventTitleEl.value = eventNames[this.value];
        }
    );
});
