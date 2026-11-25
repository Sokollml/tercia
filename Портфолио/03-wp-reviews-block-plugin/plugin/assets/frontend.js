/**
 * Front-end carousel for the reviews-block/testimonials block.
 * Vanilla JS, no dependencies. Uses native scroll-snap; JS only drives
 * autoplay, arrows and dots. Respects prefers-reduced-motion.
 *
 * @package ReviewsBlock
 */
( function () {
	'use strict';

	var reduceMotion =
		window.matchMedia &&
		window.matchMedia( '(prefers-reduced-motion: reduce)' ).matches;

	/**
	 * Initialise one carousel instance.
	 *
	 * @param {HTMLElement} root Block wrapper.
	 */
	function initCarousel( root ) {
		var viewport = root.querySelector( '.reviews-block__viewport' );
		var track = root.querySelector( '.reviews-block__track' );
		if ( ! viewport || ! track ) {
			return;
		}

		var cards = Array.prototype.slice.call(
			track.querySelectorAll( '.reviews-block__card' )
		);
		if ( cards.length === 0 ) {
			return;
		}

		var prevBtn = root.querySelector( '.reviews-block__nav--prev' );
		var nextBtn = root.querySelector( '.reviews-block__nav--next' );
		var dotsWrap = root.querySelector( '.reviews-block__dots' );

		var autoplay = root.getAttribute( 'data-autoplay' ) === 'true' && ! reduceMotion;
		var interval = parseInt( root.getAttribute( 'data-interval' ), 10 ) || 5000;
		var timer = null;

		/**
		 * How many cards are visible at once (based on layout width).
		 *
		 * @return {number} Cards per view.
		 */
		function perView() {
			var cardWidth = cards[ 0 ].getBoundingClientRect().width;
			if ( ! cardWidth ) {
				return 1;
			}
			return Math.max( 1, Math.round( viewport.clientWidth / cardWidth ) );
		}

		/**
		 * Number of "pages" (snap positions).
		 *
		 * @return {number} Page count.
		 */
		function pageCount() {
			return Math.max( 1, cards.length - perView() + 1 );
		}

		/**
		 * Current page index derived from scroll position.
		 *
		 * @return {number} Index.
		 */
		function currentIndex() {
			var cardWidth = cards[ 0 ].getBoundingClientRect().width;
			var gap = parseFloat( getComputedStyle( track ).columnGap || '0' ) || 0;
			var step = cardWidth + gap;
			if ( ! step ) {
				return 0;
			}
			return Math.round( viewport.scrollLeft / step );
		}

		/**
		 * Scroll to a card index.
		 *
		 * @param {number} index Target index.
		 */
		function goTo( index ) {
			var max = pageCount() - 1;
			if ( index < 0 ) {
				index = max;
			}
			if ( index > max ) {
				index = 0;
			}
			var cardWidth = cards[ 0 ].getBoundingClientRect().width;
			var gap = parseFloat( getComputedStyle( track ).columnGap || '0' ) || 0;
			var left = index * ( cardWidth + gap );
			viewport.scrollTo( {
				left: left,
				behavior: reduceMotion ? 'auto' : 'smooth',
			} );
		}

		/**
		 * Build navigation dots.
		 */
		function buildDots() {
			if ( ! dotsWrap ) {
				return;
			}
			dotsWrap.innerHTML = '';
			var pages = pageCount();
			for ( var i = 0; i < pages; i++ ) {
				( function ( i ) {
					var dot = document.createElement( 'button' );
					dot.type = 'button';
					dot.className = 'reviews-block__dot';
					dot.setAttribute( 'role', 'tab' );
					dot.setAttribute(
						'aria-label',
						'Отзыв ' + ( i + 1 )
					);
					dot.addEventListener( 'click', function () {
						goTo( i );
						restart();
					} );
					dotsWrap.appendChild( dot );
				} )( i );
			}
			updateDots();
		}

		/**
		 * Highlight the active dot.
		 */
		function updateDots() {
			if ( ! dotsWrap ) {
				return;
			}
			var dots = dotsWrap.querySelectorAll( '.reviews-block__dot' );
			var idx = currentIndex();
			for ( var i = 0; i < dots.length; i++ ) {
				var active = i === idx;
				dots[ i ].classList.toggle( 'is-active', active );
				dots[ i ].setAttribute( 'aria-selected', active ? 'true' : 'false' );
			}
		}

		/**
		 * Advance one page (autoplay tick).
		 */
		function tick() {
			var next = currentIndex() + 1;
			if ( next > pageCount() - 1 ) {
				next = 0;
			}
			goTo( next );
		}

		/**
		 * Start autoplay.
		 */
		function start() {
			if ( ! autoplay || timer ) {
				return;
			}
			timer = window.setInterval( tick, interval );
		}

		/**
		 * Stop autoplay.
		 */
		function stop() {
			if ( timer ) {
				window.clearInterval( timer );
				timer = null;
			}
		}

		/**
		 * Restart autoplay (used after manual interaction).
		 */
		function restart() {
			stop();
			start();
		}

		// Wire controls.
		if ( prevBtn ) {
			prevBtn.addEventListener( 'click', function () {
				goTo( currentIndex() - 1 );
				restart();
			} );
		}
		if ( nextBtn ) {
			nextBtn.addEventListener( 'click', function () {
				goTo( currentIndex() + 1 );
				restart();
			} );
		}

		// Pause on hover / focus.
		root.addEventListener( 'mouseenter', stop );
		root.addEventListener( 'mouseleave', start );
		root.addEventListener( 'focusin', stop );
		root.addEventListener( 'focusout', start );

		// Update dots as the user scrolls (debounced via rAF).
		var scrolling = false;
		viewport.addEventListener(
			'scroll',
			function () {
				if ( scrolling ) {
					return;
				}
				scrolling = true;
				window.requestAnimationFrame( function () {
					updateDots();
					scrolling = false;
				} );
			},
			{ passive: true }
		);

		// Rebuild on resize (perView may change).
		var resizeTimer = null;
		window.addEventListener( 'resize', function () {
			window.clearTimeout( resizeTimer );
			resizeTimer = window.setTimeout( function () {
				buildDots();
			}, 200 );
		} );

		// Pause when the tab is hidden.
		document.addEventListener( 'visibilitychange', function () {
			if ( document.hidden ) {
				stop();
			} else {
				start();
			}
		} );

		buildDots();
		start();
	}

	/**
	 * Boot every carousel block on the page.
	 */
	function boot() {
		var blocks = document.querySelectorAll(
			'.reviews-block--carousel'
		);
		Array.prototype.forEach.call( blocks, initCarousel );
	}

	if ( document.readyState === 'loading' ) {
		document.addEventListener( 'DOMContentLoaded', boot );
	} else {
		boot();
	}
} )();
