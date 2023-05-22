function myFunction() {

const inputElement = document.getElementById('hostFinder');
const listItems = document.querySelectorAll('#hostUl .nav-item');

inputElement.addEventListener('input', function(event) {
    const filterValue = event.target.value.toLowerCase();
    for (const item of listItems) {
        const itemName = item.textContent.toLowerCase();
        if (itemName.includes(filterValue)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    }
});
}