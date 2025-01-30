document.addEventListener('DOMContentLoaded', () => {
  // Close modal on click
  const closeButtons = document.querySelectorAll('.i-close');
  const closeModalButtons = document.querySelectorAll('.closeModalButton');

  closeButtons.forEach(element => {
    element.addEventListener('click', (e) => {
      const modals = document.querySelectorAll('.modal-accept');
      const modalForYou = document.querySelectorAll('.modal-for-you');

      modals.forEach(elem => {
        elem.style.display = 'none';
      });
      modalForYou.forEach(elem => {
        elem.style.display = 'none';
      });
    });
  });

  closeModalButtons.forEach(button => {
    button.addEventListener('click', () => {
      button.closest('.modal-accept').style.display = 'none';
    });
  });

  $('#forParents').click((e) => {
    e.preventDefault();
    $('#modalForParents').css({ display: 'flex' });
  });

  $('#forEducators').click((e) => {
    e.preventDefault();
    $('#modalForEducators').css({ display: 'flex' });
  });

  $('#forMedia').click((e) => {
    e.preventDefault();
    $('#modalForMedia').css({ display: 'flex' });
  });

  $('.hamburger-menu').click(function () {
    this.isOpen = !this.isOpen;
    document.body.style.overflowY = this.isOpen ? 'hidden' : null;

    if ($(this).hasClass('open')) {
      $(this).removeClass('open');
      $('.language').removeClass('white');
    } else {
      $('.hamburger-menu').removeClass('open');
      $(this).addClass('open');
      $('.language').addClass('white');
    }
  });

  const responseRangeInputs = document.querySelectorAll('.response-details-range-holder input[type="range"]');

  function handleInputChange(e) {
    const target = e.target.type !== 'range' ? document.getElementById('range') : e.target;
    const { min, max, value: val } = target;
    const percentage = (val - min) * 100 / (max - min);
    target.style.backgroundSize = `${percentage }% 100%`;
  }

  responseRangeInputs.forEach(input => {
    input.addEventListener('input', handleInputChange);
    handleInputChange({ target: input });
  });

  $('.btn-disable-after-click').on('click', function () {
    $(this).addClass('is-disabled');
  });
});

function submitBday() {
  let age = '';
  const Bdate = document.getElementById('id_birth_date').value;

  // Parse the date
  const parts = Bdate.split('.');
  const Bday = new Date(parts[2], parts[1] - 1, parts[0]); // Year, month (0-based), day

  // Calculate the age
  age += `${~~((Date.now() - Bday) / (31557600000)) } років`;

  // Update the HTML element
  const theBday = document.getElementById('age');
  theBday.innerHTML = age;
}
