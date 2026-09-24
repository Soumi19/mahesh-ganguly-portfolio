"use strict";

document.addEventListener("DOMContentLoaded", () => {

  /* =========================================================
     ELEMENTS
     ========================================================= */

  const nav = document.querySelector(".site-nav");

  const internalLinks = Array.from(
    document.querySelectorAll('a[href^="#"]')
  );

  const revealItems = Array.from(
    document.querySelectorAll(".reveal-section")
  );

  const sections = Array.from(
    document.querySelectorAll("main section[id]")
  );

  const navLinks = Array.from(
    document.querySelectorAll('.site-nav a[href^="#"]')
  );


  /* =========================================================
     SMOOTH INTERNAL SCROLLING
     ========================================================= */

  internalLinks.forEach((link) => {

    link.addEventListener("click", (event) => {

      const id = link.getAttribute("href");

      if (
        !id ||
        id === "#" ||
        !id.startsWith("#")
      ) {
        return;
      }

      const target = document.querySelector(id);

      if (!target) {
        return;
      }

      event.preventDefault();

      const navHeight = nav
        ? nav.getBoundingClientRect().height
        : 0;

      const offset = navHeight + 14;

      const targetTop =
        target.getBoundingClientRect().top +
        window.scrollY -
        offset;

      window.scrollTo({
        top: targetTop,
        behavior: "smooth"
      });

      try {
        history.replaceState(
          null,
          "",
          id
        );
      } catch (error) {
        // Navigation still works if history replacement is unavailable.
      }

    });

  });


  /* =========================================================
     REVEAL ANIMATION
     ========================================================= */

  const prefersReducedMotion =
    window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;


  if (
    prefersReducedMotion ||
    !("IntersectionObserver" in window)
  ) {

    revealItems.forEach((item) => {
      item.classList.add("is-visible");
    });

  } else {

    const revealObserver =
      new IntersectionObserver(
        (entries, observer) => {

          entries.forEach((entry) => {

            if (!entry.isIntersecting) {
              return;
            }

            entry.target.classList.add(
              "is-visible"
            );

            observer.unobserve(
              entry.target
            );

          });

        },
        {
          threshold: 0.08,
          rootMargin: "0px 0px -35px 0px"
        }
      );


    revealItems.forEach((item) => {
      revealObserver.observe(item);
    });

  }


  /* =========================================================
     ACTIVE NAVIGATION
     ========================================================= */

  const setActiveLink = (sectionId) => {

    navLinks.forEach((link) => {

      const linkTarget =
        link.getAttribute("href");

      const active =
        linkTarget === `#${sectionId}`;

      link.classList.toggle(
        "active",
        active
      );

      if (active) {

        link.setAttribute(
          "aria-current",
          "page"
        );

      } else {

        link.removeAttribute(
          "aria-current"
        );

      }

    });

  };


  if ("IntersectionObserver" in window) {

    const navObserver =
      new IntersectionObserver(
        (entries) => {

          const visibleSections =
            entries
              .filter(
                (entry) =>
                  entry.isIntersecting
              )
              .sort(
                (a, b) =>
                  b.intersectionRatio -
                  a.intersectionRatio
              );


          if (visibleSections.length === 0) {
            return;
          }


          setActiveLink(
            visibleSections[0].target.id
          );

        },
        {
          rootMargin:
            "-25% 0px -60% 0px",

          threshold: [
            0,
            0.05,
            0.15,
            0.3
          ]
        }
      );


    sections.forEach((section) => {
      navObserver.observe(section);
    });

  }


  /* =========================================================
     HANDLE DIRECT HASH LOAD
     ========================================================= */

  const scrollToCurrentHash = () => {

    const hash = window.location.hash;

    if (!hash || hash === "#") {
      return;
    }

    const target =
      document.querySelector(hash);

    if (!target) {
      return;
    }

    window.setTimeout(() => {

      const navHeight = nav
        ? nav.getBoundingClientRect().height
        : 0;

      const targetTop =
        target.getBoundingClientRect().top +
        window.scrollY -
        navHeight -
        14;

      window.scrollTo({
        top: targetTop,
        behavior: "auto"
      });

    }, 50);

  };


  scrollToCurrentHash();

});