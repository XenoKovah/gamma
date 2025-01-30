$(document).ready(() => {
  const $tabSwitch = $('.tabs-switcher-list-item');
  const $tabContent = $('.tabs-content-item');
  const choiceSubjectMarathonButton = $('#choiceSubjectMarathonButton');
  const choiceSubjectMarathonModal = $('#choiceSubjectMarathonModal');
  const marathonSubjectTimers = $('.marathonSubjectTimer');
  const marathonDetailLink = $('#marathonDetailLink');
  const showMarathonContractInfoButton = $('#showMarathonContractInfo');
  const marathonContractInfoModal = $('#marathonContractInfoModal');
  const closeTimerButton = $('#closeTimer');
  const timerAlert = $('#timerAlert');

  closeTimerButton.click(() => {
    timerAlert.addClass('d-none');
  });

  $('#tab1').show();

  $($tabSwitch).click(function () {
    const $tabId = $(this).data('tab');

    if (!$(this).hasClass('disabled-item')) {
      $($tabSwitch).removeClass('is-active');
      $(this).addClass('is-active');

      $($tabContent).hide();
      $(`#${ $tabId}`).show();

      if ($tabId === 'tab4' && currentPersonalMarathonStep) {
        $('.is-student-dashboard-steps').slick('slickGoTo', currentPersonalMarathonStep - 1);
      }
    }
  });

  const $subTabSwitch = $('.sub-tabs-switcher-list-item');

  $subTabSwitch.click(function () {
    const $subTabId = $(this).data('tab');
    const $subTabsContentItem = $(`#${ $subTabId}`);
    const $subTabContainer = $(this).closest('.sub-tabs-container');

    const $previousActiveItem = $subTabContainer.find('.sub-tabs-switcher-list-item.is-active');
    const $previousContentItem = $(`#${ $previousActiveItem.data('tab')}`);

    $previousActiveItem.removeClass('is-active');
    $previousContentItem.hide();

    $(this).addClass('is-active');
    $subTabsContentItem.show();
  });

  $('.dashboard-student-profile-item').click(function () {
    $(this).find('.is-dropdown-toggle').trigger('click');
  });

  $('#logoutBtn').click((e) => {
    e.preventDefault();
    $('#logoutModal').css({ display: 'flex' });
  });

  $('#onboardingBtn').click((e) => {
    e.preventDefault();
    $('#onboardingModal').css({ display: 'flex' });
  });

  function hasParameterByName(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.has(name);
  }

  const showOnboardingModal = hasParameterByName('showOnboardingModal');
  if (showOnboardingModal) {
    document.getElementById('onboardingModal').style.display = 'flex';
  }

  const calendarEl = document.getElementById('calendar');
  if (calendarEl) {
    const calendar = new FullCalendar.Calendar(calendarEl, {
      height: 500,
      headerToolbar: {
        start: 'prev,title,next',
        center: '',
        end: '',
      },
      buttonText: {
        today: 'Сьогодні',
        month: 'Місяць',
        week: 'Тиждень',
        more: 'ще',
      },
      firstDay: 1,
      views: {
        dayGrid: {
          dayMaxEventRows: 3,
        },
      },
      fixedWeekCount: false,
      initialView: 'dayGridWeek',
      expandRows: true,
      locale: 'uk',
      events: '/user/calendar/data/',
      eventTimeFormat: {
        hour: 'numeric',
        minute: '2-digit',
        meridiem: false,
      },
    });
    calendar.render();
  }

  if (choiceSubjectMarathonButton) {
    const choiceSubject = $('.choiceSubject');
    choiceSubjectMarathonButton.on('click', (e) => {
      choiceSubjectMarathonModal.css('display', 'flex');
    });
    $('#undoChoiceSubjectMarathon').on('click', (e) => {
      choiceSubjectMarathonModal.css('display', 'none');
    });

    $('#submitChoiceSubjectMarathon').on('click', (e) => {
      const selectedSubject = choiceSubject.filter(':checked');
      const data = { chosen_marathon_subject: selectedSubject.val() };
      $.ajax({
        url: createMarathonUrl,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val(),
        },
        data: JSON.stringify(data),
        success(data) {
          choiceSubjectMarathonModal.css('display', 'none');
          choiceSubjectMarathonButton.addClass('is-disabled');
          choiceSubjectMarathonButton.html(`Обраний предмет: ${data.subject_title}`);
          $('#countCompletedSprintsBySubject').html(
            `Пройдено спринтів: ${data.count_completed_sprints}`,
          );
        },
        error(response) {
          const error_message = Object.values(response.responseJSON)[0];
          $('#marathonValidationErrorMessage').removeClass('d-none');
          $('#marathonValidationErrorMessage').text(error_message);
        },
      });
    });

    choiceSubject.on('change', function () {
      choiceSubject.attr('checked', false);
      $(this).attr('checked', true);
      if ($(this).val() !== '' && $(this).val() !== null) {
        $('#submitChoiceSubjectMarathon').removeClass('is-disabled');
      } else { $('#submitChoiceSubjectMarathon').addClass('is-disabled'); }
    });
  }

  marathonSubjectTimers.each(function () {
    const timerElement = $(this);
    const endTime = moment(timerElement.data('endTime'));

    function updateTimer() {
      const currentTime = moment();

      if (currentTime >= endTime) {
        timerElement.html('Час вийшов');
      } else {
        const duration = moment.duration(endTime.diff(currentTime));
        const hours = duration.days() * 24 + duration.hours();
        const minutes = duration.minutes();
        const seconds = duration.seconds();

        const formattedHours = hours < 10 ? `0${ hours}` : hours;
        const formattedMinutes = minutes < 10 ? `0${ minutes}` : minutes;
        const formattedSeconds = seconds < 10 ? `0${ seconds}` : seconds;

        timerElement.html(`Залишилось: ${formattedHours}:${formattedMinutes}:${formattedSeconds} год.`);
      }
    }
    setInterval(updateTimer, 1000);
    updateTimer();
  });

  if (showMarathonContractInfoButton) {
    showMarathonContractInfoButton.on('click', () => {
      marathonContractInfoModal.removeClass('d-none');
      marathonContractInfoModal.css('display', 'flex');
    });
  }

  function openTab(tabName) {
    const tab = $(`#${ tabName}`);
    if (tab.length) {
      $('.tabs-content-item').hide();
      $('.tabs-switcher-list-item').removeClass('is-active');
      tab.show();
      $(`.tabs-switcher-list-item[data-tab='${ tabName }']`).addClass('is-active');
    }
  }

  function openSubTab(tabParam) {
    const subTab = $(`.sub-tabs-switcher-list-item[data-tab='${ tabParam }']`);
    const subTabContainer = subTab.closest('.sub-tabs-container');
    const previousActiveItem = subTabContainer.find('.sub-tabs-switcher-list-item.is-active');
    const previousContentItem = $(`#${ previousActiveItem.data('tab')}`);
    const subTabsContentItem = $(`#${ tabParam}`);

    $('.sub-tabs-switcher-list-item').removeClass('is-active');
    subTab.addClass('is-active');

    previousContentItem.hide();
    subTabsContentItem.show();
  }

  const urlParams = new URLSearchParams(window.location.search);
  const tabParam = urlParams.get('tab');
  if (tabParam) {
    openTab(tabParam);
  }
  const subTabParam = urlParams.get('sub-tab');
  if (subTabParam) {
    openSubTab(subTabParam);
    const keys = urlParams.keys();

    for (const key of keys) {
      urlParams.delete(key);
    }
    const newUrl = window.location.origin + window.location.pathname;
    window.history.replaceState({}, '', newUrl);

    if (subTabParam === 'sub-tab7') {
      const mascotElement = document.getElementById('root');
      if (mascotElement) {
        mascotElement.scrollIntoView({ block: 'start', behavior: 'instant' });
      }
    }
  }

  // Mascot block scripts

  const $mascotTabSwitch = $('.mascot-tabs-switcher-list-item');

  $mascotTabSwitch.click(function () {
    const $mascotTabId = $(this).data('tab');
    const $mascotTabsContentItem = $(`#${ $mascotTabId}`);
    const $mascotTabContainer = $(this).closest('.mascot-tabs-container');

    const $previousActiveItem = $mascotTabContainer.find('.mascot-tabs-switcher-list-item.is-active');
    const $previousContentItem = $(`#${ $previousActiveItem.data('tab')}`);

    $previousActiveItem.removeClass('is-active');
    $previousContentItem.hide();

    $(this).addClass('is-active');
    $mascotTabsContentItem.show();
  });

  const $onboardingVideo = $('#onboardingVideo');
  const videoSrc = $onboardingVideo.attr('src');
  $('#onboardingModalClose').on('click', () => {
    // Reset src attribute to stop video
    $onboardingVideo.attr('src', '');
    $onboardingVideo.attr('src', videoSrc);
  });

  $('.is-student-dashboard-steps').slick({
    arrows: true,
    dots: true,
    infinite: false,
    variableWidth: true,
    slidesToShow: 4,
    slidesToScroll: 4,
    prevArrow: $('.dashboard-student-steps-prev'),
    nextArrow: $('.dashboard-student-steps-next'),
  });
});
