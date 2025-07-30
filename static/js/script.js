// Define objects as an array of objects for better readability
const objects = [
    { id: 0, name: 'Person' },
    { id: 1, name: 'Bicycle' },
    { id: 2, name: 'Car' },
    { id: 3, name: 'Motorcycle' },
    { id: 4, name: 'Airplane' },
    { id: 5, name: 'Bus' },
    { id: 7, name: 'Truck' },
    { id: 16, name: 'Dog' },
    { id: 17, name: 'Horse' },
    { id: 18, name: 'Sheep' },
    { id: 19, name: 'Cow' }
  ];

  // Function to load objects into the container
  function loadObjects() {
    const objectSelect = document.getElementById('object-select');

    objects.forEach(obj => {
      const objInput = document.createElement('option');
      objInput.innerText = obj.name;
      objInput.value = obj.id;
      objInput.style.color = "white";

      objectSelect.appendChild(objInput);
      
    });
  }

loadObjects();