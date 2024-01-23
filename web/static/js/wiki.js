var url = "http://127.0.0.1:8000"

const divider = document.getElementById('divider');
const box1 = document.getElementById('box1');
const box2 = document.getElementById('box2');
const container = document.querySelector('.container');
let isDragging = false;

let containerWidth = container.clientWidth;
let initialPosition = containerWidth * 0.25; // 设置初始位置在大盒子宽度的30%处

divider.style.left = initialPosition + 'px';
box1.style.flex = '2.5';
box2.style.flex = '7.5';

divider.addEventListener('mousedown', function (e) {
    isDragging = true;
});

document.addEventListener('mousemove', function (e) {
    if (!isDragging) return;

    const containerRect = container.getBoundingClientRect();
    const mouseX = e.clientX - containerRect.left;

    // 限制分界线移动范围在大盒子内部
    if (mouseX >= 0 && mouseX <= containerWidth) {
        divider.style.left = mouseX + 'px';
        box1.style.flex = mouseX / containerWidth * 10;
        box2.style.flex = 10 - (mouseX / containerWidth * 10);
    }
});

document.addEventListener('mouseup', function (e) {
    isDragging = false;
});




