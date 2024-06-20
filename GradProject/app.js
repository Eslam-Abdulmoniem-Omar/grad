// ============= Scroll ==============
window.addEventListener("scroll", () => {
  if (window.scrollY > 300) {
    skillsProgress();
    // SCROLL NAVIGATION
  }
  scrollActive();
});

// ============= SKILLS SECTION  ==============
const overSec = document.querySelector(".overview");
const progressCircle = document.querySelectorAll(".progress");
let skillsCounter = false;

function skillsProgress() {
  if (window.scrollY < 400) {
    progressCircle.forEach((circle) => {
      let radius = circle.r.baseVal.value;
      let circumFerence = radius * 2 * Math.PI;
      let percent = circle.dataset.prog;
      let duration = Math.floor(3000 / percent);
      circle.style.strokeDasharray = circumFerence;
      circle.style.strokeDashoffset =
        circumFerence - (percent / 100) * circumFerence;
    });
    updateCirclePercent();
  }
}

function updateCirclePercent() {
  if (!skillsCounter) {
    progressCircle.forEach((circle, index) => {
      let percent = circle.dataset.prog;
      let startNum = 0;
      let duration = Math.floor(3000 / percent);
      let counter = setInterval(() => {
        startNum += 1;
        document.querySelectorAll(".circle-inner")[index].innerHTML =
          startNum + "%";
        if (startNum == parseInt(percent)) {
          clearInterval(counter);
        }
      }, duration);
    });
    skillsCounter = true;
  }
}

// ============= Navigation Bar  ==============
// const navLinks = document.querySelectorAll(".sidebar a");
// navLinks.forEach((link) => {
//   link.addEventListener("click", (e) => {
//     // Remove 'active' class from all links
//     navLinks.forEach((link) => {
//       link.classList.remove("active");
//     });

//     // Add 'active' class to the clicked link
//     e.currentTarget.classList.add("active");
//   });
// });

const sections = document.querySelectorAll("section[id]");

function scrollActive() {
  const scrollY = window.scrollY;
  sections.forEach((section) => {
    const sectionHeight = section.offsetHeight;
    const sectionTop = section.offsetTop - 300;
    const sectionBottom = sectionHeight + sectionTop;
    if (scrollY >= sectionTop && scrollY <= sectionBottom) {
      document
        .querySelector(`a[href*='${section.id}']`)
        .classList.add("active");
    } else {
      document
        .querySelector(`a[href*='${section.id}']`)
        .classList.remove("active");
    }
  });
}

// =============================================
// function fetchJSONData() {
//   fetch("../api/scripta.json")
//     .then((res) => {
//       if (!res.ok) {
//         throw new Error(`HTTP error! Status: ${res.status}`);
//       }
//       return res.json();
//     })
//     .then((data) => {
//       console.log(data);
//       const name = document.getElementsByClassName('overview__title-small')
//       name[0].innerHTML= data.GPU_Info[0].name
//     })
//     .catch((error) => console.error("Unable to fetch data:", error));
// }
// fetchJSONData();
