document.addEventListener('DOMContentLoaded', () => {

  localStorage.clear();

  mapboxgl.accessToken = 'pk.eyJ1IjoiaGFyc2ltcmFuMDEiLCJhIjoiY2xoZXFqMDYwMHVoZTNmbWhkMTVxYnJ6YyJ9.LTHSKlce9o52AbIW7W61wA';
  const geocoder = new MapboxGeocoder({
    accessToken: mapboxgl.accessToken,
    types: 'country,region,place,postcode,locality,neighborhood'
  });

  geocoder.addTo('#geocoder');

  // Get the geocoder results container.
  const results = document.getElementById('result');

  // Add geocoder result to container.
  geocoder.on('result', (e) => {
    // Update the 'result' element with the selected value.
    destinationInput = e.result.place_name
    localStorage.setItem('destinationInput', destinationInput);


  });

  const clearButton = document.querySelector('.mapboxgl-ctrl-geocoder--button');
  clearButton.remove();

  // Clear results container when search is cleared.
  geocoder.on('clear', () => {
    results.innerText = '';
  });




  const form = document.querySelector('#travel-form');
  const submitBtn = document.querySelector('#submit-btn');
  const responseDiv = document.querySelector('#response');
  const loadingDiv = document.querySelector('#loading');

  const radioButtons = document.querySelectorAll('input[name="toggle"]');
  let budgetValue = "Medium";  // Set the default value

  // Function to handle radio button change
  function handleRadioButtonChange() {
    if (this.checked) {
      budgetValue = this.value;
    }
  }

  // Add event listener to each radio button
  radioButtons.forEach(function (radio) {
    radio.addEventListener('change', handleRadioButtonChange);
  });

  // Set default value if no action has been performed
  window.addEventListener('DOMContentLoaded', function () {
    const checkedRadio = document.querySelector('input[name="toggle"]:checked');
    if (!checkedRadio) {
      budgetValue = "Medium";
    }
  });


  const labelElement_purpose = document.querySelector('label[for="color_mode_purpose"]');
  labelElement_purpose.addEventListener('click', () => {
    const isChecked = labelElement_purpose.classList.toggle('on');
    const value = isChecked ? labelElement_purpose.getAttribute('data-on') : labelElement_purpose.getAttribute('data-off');
  });

  const rangeInput = document.getElementById('myRange');
  let timeoutId;
  rangeInput.addEventListener('input', () => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      const currentValue = rangeInput.value;
    }, 500); // delay in milliseconds
  });





  submitBtn.addEventListener('click', (e) => {
    e.preventDefault();
    submitBtn.disabled = true;
    //loadingDiv.style.display = 'inline-block'; // show the spinner
    responseDiv.innerHTML = '';

    const searchInput = document.querySelector('.mapboxgl-ctrl-geocoder--input');
    localStorage.setItem('destination', searchInput.value);

    slectedValue = localStorage.getItem('selectedValue');
    selectedLanguage = localStorage.getItem('language');


    const data = {
      color_mode: budgetValue,
      color_mode_purpose: labelElement_purpose.classList.contains('on') ? labelElement_purpose.getAttribute('data-on') : labelElement_purpose.getAttribute('data-off'),
      rangeInput: rangeInput.value,
      destination: searchInput.value,
      hotelValue: slectedValue,
      language: selectedLanguage,
    };
    const datas = { "data": data }
    responseDiv.classList.add('notranslate')


    $.ajax({
      url: "chat_view/",
      type: "POST",
      data: { 'values': JSON.stringify(datas) },
      timeout: 1800000, // Set the timeout value to 30 minutes (1800000 milliseconds)
      xhrFields: {
        onprogress: function (e) {
          const html = marked(e.currentTarget.response);
          const text = `<p>${html}</p><a class="notranslate" style= "cursor:pointer; color: blue;" data-bs-toggle="modal" data-bs-target="#exampleModal">Connect to travel agent </a> Receive a FREE copy of your itinerary`;
          responseDiv.innerHTML = text;
        },
        onloadend: function (e) {
          submitBtn.disabled = false;
          loadingDiv.style.display = 'none';
          responseDiv.className = responseDiv.className.replace('notranslate', '');
        },
        error: function () {
          alert("Error Ajax");
        }
      }
    });
    


  });

});
