(function ( $ ) {
	'use strict';

	// This case is important when theme is not active
	if ( typeof qodef !== 'object' ) {
		window.qodef = {};
	}

	window.qodefCore                = {};
	qodefCore.shortcodes            = {};
	qodefCore.listShortcodesScripts = {
		qodefSwiper: qodef.qodefSwiper,
		qodefPagination: qodef.qodefPagination,
		qodefFilter: qodef.qodefFilter,
		qodefMasonryLayout: qodef.qodefMasonryLayout,
		qodefJustifiedGallery: qodef.qodefJustifiedGallery,
		qodefCustomCursor: qodefCore.qodefCustomCursor,
	};

	qodefCore.body         = $( 'body' );
	qodefCore.html         = $( 'html' );
	qodefCore.windowWidth  = $( window ).width();
	qodefCore.windowHeight = $( window ).height();
	qodefCore.scroll       = 0;

	$( document ).ready(
		function () {
			qodefCore.scroll = $( window ).scrollTop();
			qodefInlinePageStyle.init();
		}
	);

	$( window ).resize(
		function () {
			qodefCore.windowWidth  = $( window ).width();
			qodefCore.windowHeight = $( window ).height();
		}
	);

	$( window ).scroll(
		function () {
			qodefCore.scroll = $( window ).scrollTop();
		}
	);

	$( window ).load(
		function () {
			qodefParallaxItem.init();
		}
	);

	/**
	 * Check element to be in the viewport
	 */
	var qodefIsInViewport = {
		check: function ( $element, callback, onlyOnce ) {
			if ( $element.length ) {
				var offset = typeof $element.data( 'viewport-offset' ) !== 'undefined' ? $element.data( 'viewport-offset' ) : 0.15; // When item is 15% in the viewport

				var observer = new IntersectionObserver(
					function ( entries ) {
						// isIntersecting is true when element and viewport are overlapping
						// isIntersecting is false when element and viewport don't overlap
						if ( entries[0].isIntersecting === true ) {
							callback.call( $element );

							// Stop watching the element when it's initialize
							if ( onlyOnce !== false ) {
								observer.disconnect();
							}
						}
					},
					{ threshold: [offset] }
				);

				observer.observe( $element[0] );
			}
		},
	};

	qodefCore.qodefIsInViewport = qodefIsInViewport;

	var qodefScroll = {
		disable: function () {
			if ( window.addEventListener ) {
				window.addEventListener(
					'wheel',
					qodefScroll.preventDefaultValue,
					{ passive: false }
				);
			}

			// window.onmousewheel = document.onmousewheel = qodefScroll.preventDefaultValue;
			document.onkeydown = qodefScroll.keyDown;
		},
		enable: function () {
			if ( window.removeEventListener ) {
				window.removeEventListener(
					'wheel',
					qodefScroll.preventDefaultValue,
					{ passive: false }
				);
			}
			window.onmousewheel = document.onmousewheel = document.onkeydown = null;
		},
		preventDefaultValue: function ( e ) {
			e = e || window.event;
			if ( e.preventDefault ) {
				e.preventDefault();
			}
			e.returnValue = false;
		},
		keyDown: function ( e ) {
			var keys = [37, 38, 39, 40];
			for ( var i = keys.length; i--; ) {
				if ( e.keyCode === keys[i] ) {
					qodefScroll.preventDefaultValue( e );
					return;
				}
			}
		}
	};

	qodefCore.qodefScroll = qodefScroll;

	var qodefPerfectScrollbar = {
		init: function ( $holder ) {
			if ( $holder.length ) {
				qodefPerfectScrollbar.qodefInitScroll( $holder );
			}
		},
		qodefInitScroll: function ( $holder ) {
			var $defaultParams = {
				wheelSpeed: 0.6,
				suppressScrollX: true
			};

			var $ps = new PerfectScrollbar(
				$holder[0],
				$defaultParams
			);

			$( window ).resize(
				function () {
					$ps.update();
				}
			);
		}
	};

	qodefCore.qodefPerfectScrollbar = qodefPerfectScrollbar;

	var qodefInlinePageStyle = {
		init: function () {
			this.holder = $( '#luxedrive-core-page-inline-style' );

			if ( this.holder.length ) {
				var style = this.holder.data( 'style' );

				if ( style.length ) {
					$( 'head' ).append( '<style type="text/css">' + style + '</style>' );
				}
			}
		}
	};

	/**
	 * Init parallax item
	 */
	var qodefParallaxItem = {
		init: function () {
			var $items = $( '.qodef-parallax-item' );

			if ( $items.length ) {
				$items.each(
					function () {
						var $currentItem = $( this ),
							$y           = Math.floor( Math.random() * (-100 - (-25)) + (-25) );

						if ( $currentItem.hasClass( 'qodef-grid-item' ) ) {
							$currentItem.children( '.qodef-e-inner' ).attr(
								'data-parallax',
								'{"y": ' + $y + ', "smoothness": ' + '30' + '}'
							);
						} else {
							$currentItem.attr(
								'data-parallax',
								'{"y": ' + $y + ', "smoothness": ' + '30' + '}'
							);
						}
					}
				);
			}

			qodefParallaxItem.initParallax();
		},
		initParallax: function () {
			var parallaxInstances = $( '[data-parallax]' );

			if ( parallaxInstances.length && ! qodefCore.html.hasClass( 'touchevents' ) && typeof ParallaxScroll === 'object' ) {
				ParallaxScroll.init(); //initialization removed from plugin js file to have it run only on non-touch devices
			}
		},
	};

	qodefCore.qodefParallaxItem = qodefParallaxItem;

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function () {
			qodefAgeVerificationModal.init();
		}
	);

	var qodefAgeVerificationModal = {
		init: function () {
			this.holder = $( '#qodef-age-verification-modal' );

			if ( this.holder.length ) {
				var $preventHolder = this.holder.find( '.qodef-m-content-prevent' );

				if ( $preventHolder.length ) {
					var $preventYesButton = $preventHolder.find( '.qodef-prevent--yes' );

					$preventYesButton.on(
						'click',
						function () {
							var cname  = 'disabledAgeVerification';
							var cvalue = 'Yes';
							var exdays = 7;
							var d      = new Date();

							d.setTime( d.getTime() + (exdays * 24 * 60 * 60 * 1000) );
							var expires     = 'expires=' + d.toUTCString();
							document.cookie = cname + '=' + cvalue + ';' + expires + ';path=/';

							qodefAgeVerificationModal.handleClassAndScroll( 'remove' );
						}
					);
				}
			}
		},

		handleClassAndScroll: function ( option ) {
			if ( option === 'remove' ) {
				qodefCore.body.removeClass( 'qodef-age-verification--opened' );
				qodefCore.qodefScroll.enable();
			}
			if ( option === 'add' ) {
				qodefCore.body.addClass( 'qodef-age-verification--opened' );
				qodefCore.qodefScroll.disable();
			}
		},
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function () {
			qodefBackToTop.init();
		}
	);

	$( window ).on(
		'load',
		function () {
			qodefBackToTop.initScroll();
		}
	);

	var qodefBackToTop = {
		init: function () {
			this.holder = $( '#qodef-back-to-top' );

			if ( this.holder.length ) {
				// Scroll To Top
				this.holder.on(
					'click',
					function ( e ) {
						e.preventDefault();
						qodefBackToTop.animateScrollToTop();
					}
				);

				qodefBackToTop.showHideBackToTop();
			}
		},
		initScroll: function () {
			gsap.registerPlugin( ScrollTrigger );

			gsap.timeline().to(
				$( '#qodef-back-to-top .qodef-svg--back-to-top circle:nth-of-type(2)' ),
				{
					strokeDashoffset: 0,
					ease: 'none',
					scrollTrigger: {
						trigger: qodefCore.body,
						start: 'top top',
						end: 'bottom bottom',
						scrub: 1,
						// markers: true,
					}
				},
			);
		},
		animateScrollToTop: function () {
			window.scrollTo( { top: 0, behavior: 'smooth' } );
		},
		showHideBackToTop: function () {
			$( window ).scroll(
				function () {
					var $thisItem = $( this ),
						b         = $thisItem.scrollTop(),
						c         = $thisItem.height(),
						d;

					if ( b > 0 ) {
						d = b + c / 2;
					} else {
						d = 1;
					}

					if ( d < 1e3 ) {
						qodefBackToTop.addClass( 'off' );
					} else {
						qodefBackToTop.addClass( 'on' );
					}
				}
			);
		},
		addClass: function ( a ) {
			this.holder.removeClass( 'qodef--off qodef--on' );

			if ( a === 'on' ) {
				this.holder.addClass( 'qodef--on' );
			} else {
				this.holder.addClass( 'qodef--off' );
			}
		}
	};

})( jQuery );

(function ($) {
	"use strict";

	$( window ).on(
		'load',
		function () {
			qodefBackgroundText.init();
		}
	);

	$( window ).resize(
		function () {
			qodefBackgroundText.init();
		}
	);

	var qodefBackgroundText = {
		init                    : function () {
			var $holder = $( '.qodef-background-text' );

			if ($holder.length) {
				$holder.each(
					function () {
						qodefBackgroundText.responsiveOutputHandler( $( this ) );
					}
				);
			}
		},
		responsiveOutputHandler : function ($holder) {
			var breakpoints = {
				3840: 1441,
				1440: 1367,
				1366: 1025,
				1024: 1
			};

			$.each(
				breakpoints,
				function (max, min) {
					if (qodef.windowWidth <= max && qodef.windowWidth >= min) {
						qodefBackgroundText.generateResponsiveOutput( $holder, max );
					}
				}
			);
		},
		generateResponsiveOutput: function ($holder, width) {
			var $textHolder = $holder.find( '.qodef-m-background-text' );

			if ($textHolder.length) {
				$textHolder.css(
					{
						'font-size': $textHolder.data( 'size-' + width ) + 'px',
						'top'      : $textHolder.data( 'vertical-offset-' + width ) + 'px',
					}
				);
			}
		},
	};

	window.qodefBackgroundText = qodefBackgroundText;
})( jQuery );

(function ($) {
	'use strict';

	$(document).ready(function () {
		qodefCustomCursor.init();
	});

	// $(window).on(
	// 	'elementor/frontend/init',
	// 	function () {
	// 		qodefCustomCursor.init();
	// 	}
	// );

	var qodefCustomCursor = {
		cursorApended: false,
		init         : function () {
			const $dragSelectors = $('.qodef--drag-cursor');

			if ($dragSelectors.length) {
				const customCursor = qodefGlobal.vars.dragCursor;

				if (false === qodefCustomCursor.cursorApended) {
					qodefCore.html.append('<div class="qodef-m-custom-cursor qodef-m"><div class="qodef-m-custom-cursor-inner">' + customCursor + '</div></div>');
					qodefCustomCursor.cursorApended = true;
				}
				const $cursorHolder = $('.qodef-m-custom-cursor');

				if (!qodefCore.html.hasClass('touchevents')) {
					function handleMoveCursor(event) {
						$cursorHolder.css(
							{
								top : event.clientY - 60, // half of svg height
								left: event.clientX - 60, // half of svg width
							}
						);
					}

					document.addEventListener('pointermove', handleMoveCursor);

					// reset cursor selectors
					const resetCursorSelectors =
							'.qodef--drag-cursor .swiper-button-prev,' +
							'.qodef--drag-cursor .swiper-button-next,' +
							'.qodef--drag-cursor .swiper-pagination,' +
							'.qodef--drag-cursor .qodef-e-media-image a,' + // port/blog list link around image
							'.qodef--drag-cursor a:not(.woocommerce-loop-product__link),' + // product list link around image
							'.qodef--drag-cursor .qodef-e-post-link,' + // port/blog/product list link overlay
							'.qodef--drag-cursor .qodef-e-hotspot',
						$resetCursorSelectors = $(resetCursorSelectors);

					$resetCursorSelectors.css(
						{
							cursor: 'pointer',
						}
					);

					$(document).on(
						'mouseenter',
						resetCursorSelectors,
						function () {
							$cursorHolder.addClass('qodef--hide');
						}
					).on(
						'mouseleave',
						resetCursorSelectors,
						function () {
							$cursorHolder.removeClass('qodef--hide');
						}
					);

					// drag cursor selectors
					const dragSelectors = '.qodef--drag-cursor';

					$(document).on(
						'mouseenter',
						dragSelectors,
						function () {
							$cursorHolder.addClass('qodef--show');
						}
					).on(
						'mouseleave',
						dragSelectors,
						function () {
							$cursorHolder.removeClass('qodef--show');
						}
					);
				}
			}
		},
	};

	qodefCore.qodefCustomCursor = qodefCustomCursor;

})(jQuery);

(function ( $ ) {
	'use strict';

	$( window ).on(
		'load',
		function () {
			qodefUncoverFooter.init();
		}
	);

	var qodefUncoverFooter = {
		holder: '',
		init: function () {
			this.holder = $( '#qodef-page-footer.qodef--uncover' );

			if ( this.holder.length && ! qodefCore.html.hasClass( 'touchevents' ) ) {
				qodefUncoverFooter.addClass();
				qodefUncoverFooter.setHeight( this.holder );

				$( window ).resize(
					function () {
						qodefUncoverFooter.setHeight( qodefUncoverFooter.holder );
					}
				);
			}
		},
		setHeight: function ( $holder ) {
			$holder.css( 'height', 'auto' );

			var footerHeight = $holder.outerHeight();

			if ( footerHeight > 0 ) {
				$( '#qodef-page-outer' ).css(
					{
						'margin-bottom': footerHeight,
						'background-color': qodefCore.body.css( 'backgroundColor' )
					}
				);

				$holder.css( 'height', footerHeight );
			}
		},
		addClass: function () {
			qodefCore.body.addClass( 'qodef-page-footer--uncover' );
		}
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function () {
			qodefFullscreenMenu.init();
		}
	);

	$( window ).on(
		'resize',
		function () {
			qodefFullscreenMenu.handleHeaderWidth( 'resize' );
		}
	);

	var qodefFullscreenMenu = {
		init: function () {
			var $fullscreenMenuOpener = $( 'a.qodef-fullscreen-menu-opener' ),
				$menuItems            = $( '#qodef-fullscreen-area nav ul li a' );

			if ( $fullscreenMenuOpener.length ) {
				// prevent header changing width when fullscreen menu is open
				qodefFullscreenMenu.handleHeaderWidth( 'init' );

				// open popup menu
				$fullscreenMenuOpener.on(
					'click',
					function ( e ) {
						e.preventDefault();
						var $thisOpener = $( this );

						if ( ! qodefCore.body.hasClass( 'qodef-fullscreen-menu--opened' ) ) {
							qodefFullscreenMenu.openFullscreen( $thisOpener );

							$( document ).keyup(
								function ( e ) {
									if ( e.keyCode === 27 ) {
										qodefFullscreenMenu.closeFullscreen( $thisOpener );
									}
								}
							);
						} else {
							qodefFullscreenMenu.closeFullscreen( $thisOpener );
						}
					}
				);

				// open dropdowns
				$menuItems.on(
					'tap click',
					function ( e ) {
						var $thisItem = $( this );

						if ( $thisItem.parent().hasClass( 'menu-item-has-children' ) ) {
							e.preventDefault();
							qodefFullscreenMenu.clickItemWithChild( $thisItem );
						} else if ( $thisItem.attr( 'href' ) !== 'http://#' && $thisItem.attr( 'href' ) !== '#' ) {
							qodefFullscreenMenu.closeFullscreen( $fullscreenMenuOpener );
						}
					}
				);
			}
		},
		openFullscreen: function ( $opener ) {
			$opener.addClass( 'qodef--opened' );
			qodefCore.body.removeClass( 'qodef-fullscreen-menu-animate--out' ).addClass( 'qodef-fullscreen-menu--opened qodef-fullscreen-menu-animate--in' );
			qodefCore.qodefScroll.disable();
		},
		closeFullscreen: function ( $opener ) {
			$opener.removeClass( 'qodef--opened' );
			qodefCore.body.removeClass( 'qodef-fullscreen-menu--opened qodef-fullscreen-menu-animate--in' ).addClass( 'qodef-fullscreen-menu-animate--out' );
			qodefCore.qodefScroll.enable();
			$( 'nav.qodef-fullscreen-menu ul.sub_menu' ).slideUp( 200 );
		},
		clickItemWithChild: function ( thisItem ) {
			var $thisItemParent  = thisItem.parent(),
				$thisItemSubMenu = $thisItemParent.find( '.sub-menu' ).first();

			if ( $thisItemSubMenu.is( ':visible' ) ) {
				$thisItemSubMenu.slideUp( 300 );
				$thisItemParent.removeClass( 'qodef--opened' );
			} else {
				$thisItemSubMenu.slideDown( 300 );
				$thisItemParent.addClass( 'qodef--opened' ).siblings().find( '.sub-menu' ).slideUp( 400 );
			}
		},
		handleHeaderWidth: function ( state ) {
			var $header               = $( '#qodef-page-header' );
			var $fullscreenMenuOpener = $( 'a.qodef-fullscreen-menu-opener' );

			if ( $header.length && $fullscreenMenuOpener.length ) {
				// if desktop device
				if ( qodefCore.windowWidth > 1024 ) {
					// if page height is greater than window height, scroll bar is visible
					if ( qodefCore.body.height() > qodefCore.windowHeight ) {
						// on resize reset previously set inline width
						if ( 'resize' === state ) {
							$header.css( { 'width': '' } );
						}
						$header.width( $header.width() );
					}
				} else {
					// reset previously set inline width
					$header.css( { 'width': '' } );
				}
			}
		}
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function () {
			qodefHeaderScrollAppearance.init();
		}
	);

	var qodefHeaderScrollAppearance = {
		appearanceType: function () {
			return qodefCore.body.attr( 'class' ).indexOf( 'qodef-header-appearance--' ) !== -1 ? qodefCore.body.attr( 'class' ).match( /qodef-header-appearance--([\w]+)/ )[1] : '';
		},
		init: function () {
			var appearanceType = this.appearanceType();

			if ( appearanceType !== '' && appearanceType !== 'none' ) {
				qodefCore[appearanceType + 'HeaderAppearance']();
			}
		}
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
	    function () {
            qodefMobileHeaderAppearance.init();
        }
	);

	/*
	 **	Init mobile header functionality
	 */
	var qodefMobileHeaderAppearance = {
		init: function () {
			if ( qodefCore.body.hasClass( 'qodef-mobile-header-appearance--sticky' ) ) {

				var docYScroll1   = qodefCore.scroll,
					displayAmount = qodefGlobal.vars.mobileHeaderHeight + qodefGlobal.vars.adminBarHeight,
					$pageOuter    = $( '#qodef-page-outer' );

				qodefMobileHeaderAppearance.showHideMobileHeader( docYScroll1, displayAmount, $pageOuter );

				$( window ).scroll(
				    function () {
                        qodefMobileHeaderAppearance.showHideMobileHeader( docYScroll1, displayAmount, $pageOuter );
                        docYScroll1 = qodefCore.scroll;
                    }
				);

				$( window ).resize(
				    function () {
                        $pageOuter.css( 'padding-top', 0 );
                        qodefMobileHeaderAppearance.showHideMobileHeader( docYScroll1, displayAmount, $pageOuter );
                    }
				);
			}
		},
		showHideMobileHeader: function ( docYScroll1, displayAmount, $pageOuter ) {
			if ( qodefCore.windowWidth <= 1024 ) {
				if ( qodefCore.scroll > displayAmount * 2 ) {
					//set header to be fixed
					qodefCore.body.addClass( 'qodef-mobile-header--sticky' );

					//add transition to it
					setTimeout(
						function () {
							qodefCore.body.addClass( 'qodef-mobile-header--sticky-animation' );
						},
						300
					); //300 is duration of sticky header animation

					//add padding to content so there is no 'jumping'
					$pageOuter.css( 'padding-top', qodefGlobal.vars.mobileHeaderHeight );
				} else {
					//unset fixed header
					qodefCore.body.removeClass( 'qodef-mobile-header--sticky' );

					//remove transition
					setTimeout(
						function () {
							qodefCore.body.removeClass( 'qodef-mobile-header--sticky-animation' );
						},
						300
					); //300 is duration of sticky header animation

					//remove padding from content since header is not fixed anymore
					$pageOuter.css( 'padding-top', 0 );
				}

				if ( (qodefCore.scroll > docYScroll1 && qodefCore.scroll > displayAmount) || (qodefCore.scroll < displayAmount * 3) ) {
					//show sticky header
					qodefCore.body.removeClass( 'qodef-mobile-header--sticky-display' );
				} else {
					//hide sticky header
					qodefCore.body.addClass( 'qodef-mobile-header--sticky-display' );
				}
			}
		}
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function () {
			qodefNavMenu.init();
		}
	);

	var qodefNavMenu = {
		init: function () {
			qodefNavMenu.dropdownBehavior();
			qodefNavMenu.wideDropdownPosition();
			qodefNavMenu.dropdownPosition();
		},
		dropdownBehavior: function () {
			var $menuItems = $( '.qodef-header-navigation > ul > li' );

			$menuItems.each(
				function () {
					var $thisItem = $( this );

					if ( $thisItem.find( '.qodef-drop-down-second' ).length ) {
						qodef.qodefWaitForImages.check(
							$thisItem,
							function () {
								var $dropdownHolder      = $thisItem.find( '.qodef-drop-down-second' ),
									$dropdownMenuItem    = $dropdownHolder.find( '.qodef-drop-down-second-inner ul' ),
									dropDownHolderHeight = $dropdownMenuItem.outerHeight();

								if ( navigator.userAgent.match( /(iPod|iPhone|iPad)/ ) ) {
									$thisItem.on(
										'touchstart mouseenter',
										function () {
											$dropdownHolder.css(
												{
													'height': dropDownHolderHeight,
													'overflow': 'visible',
													'visibility': 'visible',
													'opacity': '1',
												}
											);
										}
									).on(
										'mouseleave',
										function () {
											$dropdownHolder.css(
												{
													'height': '0px',
													'overflow': 'hidden',
													'visibility': 'hidden',
													'opacity': '0',
												}
											);
										}
									);
								} else {
									if ( qodefCore.body.hasClass( 'qodef-drop-down-second--animate-height' ) ) {
										var animateConfig = {
											interval: 0,
											over: function () {
												setTimeout(
													function () {
														$dropdownHolder.addClass( 'qodef-drop-down--start' ).css(
															{
																'visibility': 'visible',
																'height': '0',
																'opacity': '1',
															}
														);
														$dropdownHolder.stop().animate(
															{
																'height': dropDownHolderHeight,
															},
															400,
															'linear',
															function () {
																$dropdownHolder.css( 'overflow', 'visible' );
															}
														);
													},
													100
												);
											},
											timeout: 100,
											out: function () {
												$dropdownHolder.stop().animate(
													{
														'height': '0',
														'opacity': 0,
													},
													100,
													function () {
														$dropdownHolder.css(
															{
																'overflow': 'hidden',
																'visibility': 'hidden',
															}
														);
													}
												);

												$dropdownHolder.removeClass( 'qodef-drop-down--start' );
											}
										};

										$thisItem.hoverIntent( animateConfig );
									} else {
										var config = {
											interval: 0,
											over: function () {
												setTimeout(
													function () {
														$dropdownHolder.addClass( 'qodef-drop-down--start' ).stop().css( { 'height': dropDownHolderHeight } );
													},
													150
												);
											},
											timeout: 150,
											out: function () {
												$dropdownHolder.stop().css( { 'height': '0' } ).removeClass( 'qodef-drop-down--start' );
											}
										};

										$thisItem.hoverIntent( config );
									}
								}
							}
						);
					}
				}
			);
		},
		wideDropdownPosition: function () {
			var $menuItems = $( '.qodef-header-navigation > ul > li.qodef-menu-item--wide' );

			if ( $menuItems.length ) {
				$menuItems.each(
					function () {
						var $menuItem        = $( this );
						var $menuItemSubMenu = $menuItem.find( '.qodef-drop-down-second' );

						if ( $menuItemSubMenu.length ) {
							$menuItemSubMenu.css( 'left', 0 );

							var leftPosition = $menuItemSubMenu.offset().left;

							if ( qodefCore.body.hasClass( 'qodef--boxed' ) ) {
								//boxed layout case
								var boxedWidth = $( '.qodef--boxed #qodef-page-wrapper' ).outerWidth();
								leftPosition   = leftPosition - (qodefCore.windowWidth - boxedWidth) / 2;
								$menuItemSubMenu.css( { 'left': -leftPosition, 'width': boxedWidth } );

							} else if ( qodefCore.body.hasClass( 'qodef-drop-down-second--full-width' ) ) {
								//wide dropdown full width case
								$menuItemSubMenu.css( { 'left': -leftPosition, 'width': qodefCore.windowWidth } );
							} else {
								//wide dropdown in grid case
								$menuItemSubMenu.css( { 'left': -leftPosition + (qodefCore.windowWidth - $menuItemSubMenu.width()) / 2 } );
							}
						}
					}
				);
			}
		},
		dropdownPosition: function () {
			var $menuItems = $( '.qodef-header-navigation > ul > li.qodef-menu-item--narrow.menu-item-has-children' );

			if ( $menuItems.length ) {
				$menuItems.each(
					function () {
						var $thisItem         = $( this ),
							menuItemPosition  = $thisItem.offset().left,
							$dropdownHolder   = $thisItem.find( '.qodef-drop-down-second' ),
							$dropdownMenuItem = $dropdownHolder.find( '.qodef-drop-down-second-inner ul' ),
							dropdownMenuWidth = $dropdownMenuItem.outerWidth(),
							menuItemFromLeft  = $( window ).width() - menuItemPosition;

						if ( qodef.body.hasClass( 'qodef--boxed' ) ) {
							//boxed layout case
							var boxedWidth   = $( '.qodef--boxed #qodef-page-wrapper' ).outerWidth();
							menuItemFromLeft = boxedWidth - menuItemPosition;
						}

						var dropDownMenuFromLeft;

						if ( $thisItem.find( 'li.menu-item-has-children' ).length > 0 ) {
							dropDownMenuFromLeft = menuItemFromLeft - dropdownMenuWidth;
						}

						$dropdownHolder.removeClass( 'qodef-drop-down--right' );
						$dropdownMenuItem.removeClass( 'qodef-drop-down--right' );
						if ( menuItemFromLeft < dropdownMenuWidth || dropDownMenuFromLeft < dropdownMenuWidth ) {
							$dropdownHolder.addClass( 'qodef-drop-down--right' );
							$dropdownMenuItem.addClass( 'qodef-drop-down--right' );
						}
					}
				);
			}
		}
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	$( window ).on(
		'load',
		function () {
			qodefParallaxBackground.init();
		}
	);

	/**
	 * Init global parallax background functionality
	 */
	var qodefParallaxBackground = {
		init: function ( settings ) {
			this.$sections = $( '.qodef-parallax' );

			// Allow overriding the default config
			$.extend( this.$sections, settings );

			var isSupported = ! qodefCore.html.hasClass( 'touchevents' ) && ! qodefCore.body.hasClass( 'qodef-browser--edge' ) && ! qodefCore.body.hasClass( 'qodef-browser--ms-explorer' );

			if ( this.$sections.length && isSupported ) {
				this.$sections.each(
					function () {
						qodefParallaxBackground.ready( $( this ) );
					}
				);
			}
		},
		ready: function ( $section ) {
			$section.$imgHolder  = $section.find( '.qodef-parallax-img-holder' );
			$section.$imgWrapper = $section.find( '.qodef-parallax-img-wrapper' );
			$section.$img        = $section.find( 'img.qodef-parallax-img' );

			var h           = $section.height(),
				imgWrapperH = $section.$imgWrapper.height();

			$section.movement = 100 * (imgWrapperH - h) / h / 2; //percentage (divided by 2 due to absolute img centering in CSS)

			$section.buffer       = window.scrollY;
			$section.scrollBuffer = null;


			//calc and init loop
			requestAnimationFrame(
				function () {
					$section.$imgHolder.animate( { opacity: 1 }, 100 );
					qodefParallaxBackground.calc( $section );
					qodefParallaxBackground.loop( $section );
				}
			);

			//recalc
			$( window ).on(
				'resize',
				function () {
					qodefParallaxBackground.calc( $section );
				}
			);
		},
		calc: function ( $section ) {
			var wH = $section.$imgWrapper.height(),
				wW = $section.$imgWrapper.width();

			if ( $section.$img.width() < wW ) {
				$section.$img.css(
					{
						'width': '100%',
						'height': 'auto',
					}
				);
			}

			if ( $section.$img.height() < wH ) {
				$section.$img.css(
					{
						'height': '100%',
						'width': 'auto',
						'max-width': 'unset',
					}
				);
			}
		},
		loop: function ( $section ) {
			if ( $section.scrollBuffer === Math.round( window.scrollY ) ) {
				requestAnimationFrame(
					function () {
						qodefParallaxBackground.loop( $section );
					}
				); //repeat loop

				return false; //same scroll value, do nothing
			} else {
				$section.scrollBuffer = Math.round( window.scrollY );
			}

			var wH   = window.outerHeight,
				sTop = $section.offset().top,
				sH   = $section.height();

			if ( $section.scrollBuffer + wH * 1.2 > sTop && $section.scrollBuffer < sTop + sH ) {
				var delta = (Math.abs( $section.scrollBuffer + wH - sTop ) / (wH + sH)).toFixed( 4 ), //coeff between 0 and 1 based on scroll amount
					yVal  = (delta * $section.movement).toFixed( 4 );

				if ( $section.buffer !== delta ) {
					$section.$imgWrapper.css( 'transform', 'translate3d(0,' + yVal + '%, 0)' );
				}

				$section.buffer = delta;
			}

			requestAnimationFrame(
				function () {
					qodefParallaxBackground.loop( $section );
				}
			); //repeat loop
		}
	};

	qodefCore.qodefParallaxBackground = qodefParallaxBackground;

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function () {
			qodefReview.init();
		}
	);

	var qodefReview = {
		init: function () {
			var ratingHolder = $( '#qodef-page-comments-form .qodef-rating-inner' );

			var addActive = function ( stars, ratingValue ) {
				for ( var i = 0; i < stars.length; i++ ) {
					var star = stars[i];

					if ( i < ratingValue ) {
						$( star ).addClass( 'active' );
					} else {
						$( star ).removeClass( 'active' );
					}
				}
			};

			ratingHolder.each(
				function () {
					var thisHolder  = $( this ),
						ratingInput = thisHolder.find( '.qodef-rating' ),
						ratingValue = ratingInput.val(),
						stars       = thisHolder.find( '.qodef-star-rating' );

					addActive( stars, ratingValue );

					stars.on(
						'click',
						function () {
							ratingInput.val( $( this ).data( 'value' ) ).trigger( 'change' );
						}
					);

					ratingInput.change(
						function () {
							ratingValue = ratingInput.val();

							addActive( stars, ratingValue );
						}
					);
				}
			);
		}
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function () {
			qodefSideArea.init();
		}
	);

	var qodefSideArea = {
		init: function () {
			var $sideAreaOpener = $( 'a.qodef-side-area-opener' ),
				$sideAreaClose  = $( '#qodef-side-area-close' ),
				$sideArea       = $( '#qodef-side-area' );

			qodefSideArea.openerHoverColor( $sideAreaOpener );

			// Open Side Area
			$sideAreaOpener.on(
				'click',
				function ( e ) {
					e.preventDefault();

					if ( ! qodefCore.body.hasClass( 'qodef-side-area--opened' ) ) {
						qodefSideArea.openSideArea();

						$( document ).keyup(
							function ( e ) {
								if ( e.keyCode === 27 ) {
									qodefSideArea.closeSideArea();
								}
							}
						);
					} else {
						qodefSideArea.closeSideArea();
					}
				}
			);

			$sideAreaClose.on(
				'click',
				function ( e ) {
					e.preventDefault();
					qodefSideArea.closeSideArea();
				}
			);

			if ( $sideArea.length && typeof qodefCore.qodefPerfectScrollbar === 'object' ) {
				qodefCore.qodefPerfectScrollbar.init( $sideArea );
			}
		},
		openSideArea: function () {
			var $wrapper      = $( '#qodef-page-wrapper' );
			var currentScroll = $( window ).scrollTop();

			$( '.qodef-side-area-cover' ).remove();
			$wrapper.prepend( '<div class="qodef-side-area-cover"/>' );
			qodefCore.body.removeClass( 'qodef-side-area-animate--out' ).addClass( 'qodef-side-area--opened qodef-side-area-animate--in' );

			$( '.qodef-side-area-cover' ).on(
				'click',
				function ( e ) {
					e.preventDefault();
					qodefSideArea.closeSideArea();
				}
			);

			$( window ).scroll(
				function () {
					if ( Math.abs( qodefCore.scroll - currentScroll ) > 400 ) {
						qodefSideArea.closeSideArea();
					}
				}
			);
		},
		closeSideArea: function () {
			qodefCore.body.removeClass( 'qodef-side-area--opened qodef-side-area-animate--in' ).addClass( 'qodef-side-area-animate--out' );
		},
		openerHoverColor: function ( $opener ) {
			if ( typeof $opener.data( 'hover-color' ) !== 'undefined' ) {
				var hoverColor    = $opener.data( 'hover-color' );
				var originalColor = $opener.css( 'color' );

				$opener.on(
					'mouseenter',
					function () {
						$opener.css( 'color', hoverColor );
					}
				).on(
					'mouseleave',
					function () {
						$opener.css( 'color', originalColor );
					}
				);
			}
		}
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function () {
			qodefSpinner.init();
		}
	);

	$( window ).on(
		'load',
		function () {
			qodefSpinner.windowLoaded = true;
		}
	);

	$( window ).on(
		'elementor/frontend/init',
		function () {
			var isEditMode = Boolean( elementorFrontend.isEditMode() );

			if ( isEditMode ) {
				qodefSpinner.init( isEditMode );
			}
		}
	);

	var qodefSpinner = {
		holder: '',
		windowLoaded: false,
		preloaderFinished: false,
		percentNumber: 0,
		init: function ( isEditMode ) {
			this.holder = $( '#qodef-page-spinner:not(.qodef--custom-spinner):not(.qodef-layout--textual)' );

			if ( this.holder.length ) {
				if ( this.holder.hasClass( 'qodef-layout--luxedrive' ) ) {

					var tl = gsap.timeline();

					tl.to(
						qodefSpinner.holder.find( '.qodef-m-spinner-loading-progress' ),
						{
							innerText: 100,
							snap: {
								innerText: 1
							},
							duration: 3,
							delay: 0.5,
						},
						'qodef-spinner-start'
					);
					tl.to(
						qodefSpinner.holder.find( '.qodef-m-spinner-bar-active' ),
						{
							scaleX: 1,
							duration: 3,
							delay: 0.5,
						},
						'qodef-spinner-start'
					);

					tl.to(
						qodefSpinner.holder.find( '.qode-m-spinner-logo' ),
						{
							opacity: 1,
							x: 0,
							duration: 0.8,
						},
						'qodef-spinner-show'
					);
					tl.to(
						qodefSpinner.holder.find( '.qodef-m-spinner-number' ),
						{
							color: 'var(--qode-main-color)',
						},
						'qodef-spinner-show'
					);

					tl.to(
						qodefSpinner.holder,
						{
							yPercent: -110,
							duration: .8,
							delay: .3,
							onComplete: () => {
								qodefSpinner.preloaderFinished = true;
								qodefSpinner.animateSpinner(
									isEditMode,
									true
								);
								qodefSpinner.fadeOutAnimation();
							}
						},
						'qodef-spinner-end'
					);

				} else {
					qodefSpinner.preloaderFinished = true;
					qodefSpinner.animateSpinner(
						isEditMode,
						false
					);
					qodefSpinner.fadeOutAnimation();
				}
			}
		},
		animateSpinner: function ( isEditMode, flag ) {

			var qodefLoadInterval = setInterval(
				function () {
					if ( qodefSpinner.windowLoaded && qodefSpinner.preloaderFinished ) {
						clearInterval( qodefLoadInterval );

						if ( flag ) {
							qodefSpinner.holder.addClass( 'qodef--end' );
						} else {
							qodefSpinner.fadeOutLoader();
						}
					}
				},
				100
			);

			if ( isEditMode ) {
				qodefSpinner.fadeOutLoader();
			}
		},
		fadeOutLoader: function ( speed, delay, easing ) {
			var $holder = qodefSpinner.holder.length ? qodefSpinner.holder : $( '#qodef-page-spinner:not(.qodef--custom-spinner):not(.qodef-layout--textual)' );

			speed  = speed ? speed : 600;
			delay  = delay ? delay : 0;
			easing = easing ? easing : 'swing';

			$holder.delay( delay ).fadeOut(
				speed,
				easing
			);

			$( window ).on(
				'bind',
				'pageshow',
				function ( event ) {
					if ( event.originalEvent.persisted ) {
						$holder.fadeOut(
							speed,
							easing
						);
					}
				}
			);
		},
		fadeOutAnimation: function () {

			// Check for fade out animation
			if ( qodefCore.body.hasClass( 'qodef-spinner--fade-out' ) ) {
				var $pageHolder = $( '#qodef-page-wrapper' ),
					$linkItems  = $( 'a' );

				// If back button is pressed, then show content to avoid state where content is on display:none
				window.addEventListener(
					'pageshow',
					function ( event ) {
						var historyPath = event.persisted || (typeof window.performance !== 'undefined' && window.performance.navigation.type === 2);
						if ( historyPath && ! $pageHolder.is( ':visible' ) ) {
							$pageHolder.show();
						}
					}
				);

				$linkItems.on(
					'click',
					function ( e ) {
						var $clickedLink = $( this );

						if (
							e.which === 1 && // check if the left mouse button has been pressed
							$clickedLink.attr( 'href' ).indexOf( window.location.host ) >= 0 && // check if the link is to the same domain
							! $clickedLink.hasClass( 'remove' ) && // check is WooCommerce remove link
							$clickedLink.parent( '.product-remove' ).length <= 0 && // check is WooCommerce remove link
							$clickedLink.parents( '.woocommerce-product-gallery__image' ).length <= 0 && // check is product gallery link
							typeof $clickedLink.data( 'rel' ) === 'undefined' && // check pretty photo link
							typeof $clickedLink.attr( 'rel' ) === 'undefined' && // check VC pretty photo link
							! $clickedLink.hasClass( 'lightbox-active' ) && // check is lightbox plugin active
							(typeof $clickedLink.attr( 'target' ) === 'undefined' || $clickedLink.attr( 'target' ) === '_self') && // check if the link opens in the same window
							$clickedLink.attr( 'href' ).split( '#' )[0] !== window.location.href.split( '#' )[0] // check if it is an anchor aiming for a different page
						) {
							e.preventDefault();

							$pageHolder.fadeOut(
								600,
								'swing',
								function () {
									window.location = $clickedLink.attr( 'href' );
								}
							);
						}
					}
				);
			}
		}
	};

})( jQuery );

(function ($) {
	"use strict";

	$(window).on('load', function () {
		qodefStickyColumn.init('init');
	});

	$(window).resize(function () {
		qodefStickyColumn.init('resize');
	});

	var qodefStickyColumn = {
		pageOffset: '',
		scrollAmount: '',

		init: function (state) {
			var $holder = $('.qodef-sticky-column'),
				editor = $holder.hasClass('wpb_column') ? 'wp_bakery' : 'elementor';

			if ($holder.length) {
				$holder.each(function () {
					qodefStickyColumn.calculateVars($(this), state, editor);
				});
			}
		},
		calculateVars: function ($column, state, editor) {
			var columnVars = {};

			if ('wp_bakery' === editor) {
				columnVars.$columnInner = $column.find('.vc_column-inner');
			} else {
				columnVars.$columnInner = $column.find('>.elementor-column-wrap');
				if ( ! columnVars.$columnInner.length ) {
					columnVars.$columnInner = $column.find('>.elementor-widget-wrap');
				}
			}

			columnVars.columnTopEdgePosition = $column.offset().top;
			columnVars.columnLeftEdgePosition = $column.offset().left;
			columnVars.columnWidth = $column.innerWidth();
			columnVars.columnHeight = columnVars.$columnInner.outerHeight(true);

			if ('wp_bakery' === editor) {
				columnVars.$row = $column.closest('.vc_row');
			} else {
				columnVars.$row = $column.closest('.elementor-section');
			}

			columnVars.rowTopEdgePosition = columnVars.$row.offset().top;
			columnVars.rowHeight = columnVars.$row.outerHeight(true);
			columnVars.rowBottomEdgePosition = columnVars.rowTopEdgePosition + columnVars.rowHeight;
			qodefStickyColumn.scrollAmount = qodef.scroll;
			qodefStickyColumn.scrollAmount = $('#qodef-page-header').outerHeight();

			qodefStickyColumn.checkPosition( $column, columnVars);

			$(window).scroll(function () {
				if ('init' === state) {
					var scrollDirection = qodefStickyColumn.checkScrollDirection();
				}

				qodefStickyColumn.checkPosition( $column, columnVars, scrollDirection);
			});
		},
		checkPosition: function (column, columnVars, direction) {

			if (qodef.windowWidth > 1024) {
				qodefStickyColumn.calculateOffset();

				if ( column.hasClass('qodef-sticky-fixed') ) {
					qodefStickyColumn.setPosition(columnVars, 'fixed');
				} else {
					if ((qodef.scroll + qodefStickyColumn.pageOffset) <= columnVars.columnTopEdgePosition) {
						qodefStickyColumn.setPosition(columnVars, 'relative');
					}
					
					if (((qodef.scroll + qodefStickyColumn.pageOffset) >= columnVars.columnTopEdgePosition) && ((qodef.scroll + qodefStickyColumn.pageOffset + columnVars.columnHeight) < columnVars.rowBottomEdgePosition)) {
						qodefStickyColumn.setPosition(columnVars, 'fixed', direction);
					} else if ((qodef.scroll + qodefStickyColumn.pageOffset + columnVars.columnHeight) >= columnVars.rowBottomEdgePosition) {
						if ( column.parents('.qodef-custom-scroll-fix').length ) {
							qodefStickyColumn.setPosition(columnVars, 'fixed', direction);
						} else {
							qodefStickyColumn.setPosition(columnVars, 'absolute');
						}
					}
				}

			} else {
				qodefStickyColumn.setPosition(columnVars, 'relative');
			}
		},
		calculateOffset: function () {
			qodefStickyColumn.pageOffset = 0;

			if ($('body').hasClass('admin-bar')) {
				qodefStickyColumn.pageOffset += 32;
			}

			if ($('body').hasClass('qodef-header--sticky-display') && $('.qodef-header-sticky').length) {
				qodefStickyColumn.pageOffset += parseInt($('.qodef-header-sticky').outerHeight(true));
			}
		},
		checkScrollDirection: function () {
			var scrollDirection = (qodef.scroll > qodefStickyColumn.scrollAmount) ? 'down' : 'up';

			qodefStickyColumn.scrollAmount = qodef.scroll;

			return scrollDirection;
		},
		setPosition: function (columnVars, position, direction) {
			if ('relative' === position) {
				columnVars.$columnInner.css({
					'bottom': 'auto',
					'left': 'auto',
					'position': 'relative',
					'top': 'auto',
					'width': columnVars.columnWidth,
					'transform': 'translateY(0)',
					'transition': 'none'
				});
			}
			if ('fixed' === position) {
				var transitionValue = 'none';
				
				if ($('body').hasClass('qodef-header--sticky-display')) {
					transitionValue = ('up' === direction) ? 'none' : 'transform .5s ease';
				}
				
				columnVars.$columnInner.css({
					'bottom': 'auto',
					'left': columnVars.columnLeftEdgePosition,
					'position': 'fixed',
					'top': 0,
					'width': columnVars.columnWidth,
					'transform': 'translateY(' + qodefStickyColumn.pageOffset + 'px)',
					'transition': transitionValue
				});
				
			}
			if ('absolute' === position) {
				columnVars.$columnInner.css({
					'bottom': -columnVars.rowHeight,
					'left': '0',
					'position': 'absolute',
					'top': 'auto',
					'width': columnVars.columnWidth,
					'transform': 'translateY(0)',
					'transition': 'none'
				});
			}
		}
	};

	window.qodefStickyColumn = qodefStickyColumn;
})(jQuery);

(function ( $ ) {
	'use strict';

	$( window ).on(
		'load',
		function () {
			qodefSubscribeModal.init();
		}
	);

	var qodefSubscribeModal = {
		init: function () {
			this.holder = $( '#qodef-subscribe-popup-modal' );

			if ( this.holder.length ) {
				var $preventHolder = this.holder.find( '.qodef-sp-prevent' ),
					$modalClose    = $( '.qodef-sp-close' ),
					disabledPopup  = 'no';

				if ( $preventHolder.length ) {
					var isLocalStorage = this.holder.hasClass( 'qodef-sp-prevent-cookies' ),
						$preventInput  = $preventHolder.find( '.qodef-sp-prevent-input' ),
						preventValue   = $preventInput.data( 'value' );

					if ( isLocalStorage ) {
						disabledPopup = localStorage.getItem( 'disabledPopup' );
						sessionStorage.removeItem( 'disabledPopup' );
					} else {
						disabledPopup = sessionStorage.getItem( 'disabledPopup' );
						localStorage.removeItem( 'disabledPopup' );
					}

					$preventHolder.children().on(
						'click',
						function () {
							if ( preventValue !== 'yes' ) {
								preventValue = 'yes';
								$preventInput.addClass( 'qodef-sp-prevent-clicked' ).data( 'value', 'yes' );
							} else {
								preventValue = 'no';
								$preventInput.removeClass( 'qodef-sp-prevent-clicked' ).data( 'value', 'no' );
							}

							if ( preventValue === 'yes' ) {
								if ( isLocalStorage ) {
									localStorage.setItem( 'disabledPopup', 'yes' );
								} else {
									sessionStorage.setItem( 'disabledPopup', 'yes' );
								}
							} else {
								if ( isLocalStorage ) {
									localStorage.setItem( 'disabledPopup', 'no' );
								} else {
									sessionStorage.setItem( 'disabledPopup', 'no' );
								}
							}
						}
					);
				}

				if ( disabledPopup !== 'yes' ) {
					if ( qodefCore.body.hasClass( 'qodef-sp-opened' ) ) {
						qodefSubscribeModal.handleClassAndScroll( 'remove' );
					} else {
						qodefSubscribeModal.handleClassAndScroll( 'add' );
					}

					$modalClose.on(
						'click',
						function ( e ) {
							e.preventDefault();

							qodefSubscribeModal.handleClassAndScroll( 'remove' );
						}
					);

					// Close on escape
					$( document ).keyup(
						function ( e ) {
							if ( e.keyCode === 27 ) { // KeyCode for ESC button is 27
								qodefSubscribeModal.handleClassAndScroll( 'remove' );
							}
						}
					);
				}
			}
		},

		handleClassAndScroll: function ( option ) {
			if ( option === 'remove' ) {
				qodefCore.body.removeClass( 'qodef-sp-opened' );
				qodefCore.qodefScroll.enable();
			}

			if ( option === 'add' ) {
				qodefCore.body.addClass( 'qodef-sp-opened' );
				qodefCore.qodefScroll.disable();
			}
		},
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	$( window ).on(
		'load',
		function () {
			qodefUncoveringSection.init();
		}
	);

	$( window ).resize(
		function () {
			qodefUncoveringSection.init();
		}
	);

	var qodefUncoveringSection = {
		init: function () {
			var $uncoveringSection = $( '.qodef-uncovering-section' );

			if ( $uncoveringSection.length ) {
				var $sectionHolder = $uncoveringSection.find( '.qodef-page-content-section > .elementor' ),
					$lastSection   = $( '.qodef-page-content-section > .elementor > .elementor-section:last-child' );

				if ( $sectionHolder.length && $lastSection.length ) {
					var lastSectionHeight = $lastSection.outerHeight();

					$sectionHolder.css( { 'margin-bottom': lastSectionHeight + 'px' } );
				}
			}
		},
	};

	qodefCore.qodefUncoveringSection = qodefUncoveringSection;

})( jQuery );

(function ($) {
	'use strict';

	$(window).on(
		'load',
		function () {
			qodefVehicleBookingFormPosition.init();
		}
	);

	var qodefVehicleBookingFormPosition = {
		init: function () {
			var $opener  = $('.single-vehicle .qodef-vehicle-item .qodef-booking-form-opener .qodef-button'),
				$overlay = $('.single-vehicle .qodef-vehicle-item .qodef-booking-form-overlay'),
				$holder  = $('.single-vehicle .qodef-vehicle-item .qodef-booking-form-wrapper'),
				$close   = $('.single-vehicle .qodef-vehicle-item .qodef-booking-form-wrapper .qodef-booking-form-close');

			var closeOnScroll = function(event){
				event.preventDefault();

				if ( $holder.hasClass( 'qodef--active' ) ) {
					$holder.removeClass( 'qodef--active' );
					document.removeEventListener('scroll', closeOnScroll);
				}
			};

			if ($opener.length) {
				$opener.on(
					'click',
					function (event) {
						event.preventDefault();

						if ( ! $holder.hasClass( 'qodef--active' ) ) {
							$holder.addClass( 'qodef--active' );

							if( qodefCore.windowWidth > 680 ) {
								document.addEventListener( 'scroll', closeOnScroll );
							}
						}
					}
				);
				$overlay.add( $close ).on(
					'click',
					function() {
						if ( $holder.hasClass( 'qodef--active' ) ) {
							$holder.removeClass( 'qodef--active' );
						}
					}
				);
			}
		}
	};

})(jQuery);

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_accordion = {};

	$( document ).ready(
		function () {
			qodefAccordion.init();
		}
	);

	var qodefAccordion = {
		init: function () {
			var $holder = $( '.qodef-accordion' );

			if ( $holder.length ) {
				$holder.each(
					function () {
						qodefAccordion.initItem( $( this ) );
					}
				);
			}
		},
		initItem: function ( $currentItem ) {
			if ( $currentItem.hasClass( 'qodef-behavior--accordion' ) ) {
				qodefAccordion.initAccordion( $currentItem );
			}

			if ( $currentItem.hasClass( 'qodef-behavior--toggle' ) ) {
				qodefAccordion.initToggle( $currentItem );
			}

			$currentItem.addClass( 'qodef--init' );
		},
		initAccordion: function ( $accordion ) {
			$accordion.accordion(
				{
					animate: 'swing',
					collapsible: true,
					active: 0,
					icons: '',
					heightStyle: 'content',
				}
			);
		},
		initToggle: function ( $toggle ) {
			var $toggleAccordionTitle = $toggle.find( '.qodef-accordion-title' );

			$toggleAccordionTitle.off().on(
				'mouseenter',
				function () {
					$( this ).addClass( 'ui-state-hover' );
				}
			).on(
				'mouseleave',
				function () {
					$( this ).removeClass( 'ui-state-hover' );
				}
			).on(
				'click',
				function ( e ) {
					e.preventDefault();
					e.stopImmediatePropagation();

					var $thisTitle = $( this );

					if ( $thisTitle.hasClass( 'ui-state-active' ) ) {
						$thisTitle.removeClass( 'ui-state-active' );
						$thisTitle.next().removeClass( 'ui-accordion-content-active' ).slideUp( 300 );
					} else {
						$thisTitle.addClass( 'ui-state-active' );
						$thisTitle.next().addClass( 'ui-accordion-content-active' ).slideDown( 400 );
					}
				}
			);
		}
	};

	qodefCore.shortcodes.luxedrive_core_accordion.qodefAccordion = qodefAccordion;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_button = {};

	$( document ).ready(
		function () {
			qodefButton.init();
		}
	);

	var qodefButton = {
		init: function () {
			this.buttons = $( '.qodef-button' );

			if ( this.buttons.length ) {
				this.buttons.each(
					function () {
						qodefButton.initItem( $( this ) );
					}
				);
			}
		},
		initItem: function ( $currentItem ) {
			qodefButton.buttonHoverColor( $currentItem );
			qodefButton.buttonHoverBgColor( $currentItem );
			qodefButton.buttonHoverBorderColor( $currentItem );
		},
		buttonHoverColor: function ( $button ) {
			if ( typeof $button.data( 'hover-color' ) !== 'undefined' ) {
				var hoverColor    = $button.data( 'hover-color' );
				var originalColor = $button.css( 'color' );

				$button.on(
					'mouseenter touchstart',
					function () {
						qodefButton.changeColor( $button, 'color', hoverColor );
					}
				);
				$button.on(
					'mouseleave touchend',
					function () {
						qodefButton.changeColor( $button, 'color', originalColor );
					}
				);
			}
		},
		buttonHoverBgColor: function ( $button ) {
			if ( typeof $button.data( 'hover-background-color' ) !== 'undefined' ) {
				var hoverBackgroundColor    = $button.data( 'hover-background-color' );
				var originalBackgroundColor = $button.css( 'background-color' );

				$button.on(
					'mouseenter touchstart',
					function () {
						qodefButton.changeColor( $button, 'background-color', hoverBackgroundColor );
					}
				);
				$button.on(
					'mouseleave touchend',
					function () {
						qodefButton.changeColor( $button, 'background-color', originalBackgroundColor );
					}
				);
			}
		},
		buttonHoverBorderColor: function ( $button ) {
			if ( typeof $button.data( 'hover-border-color' ) !== 'undefined' ) {
				var hoverBorderColor    = $button.data( 'hover-border-color' );
				var originalBorderColor = $button.css( 'borderTopColor' );

				$button.on(
					'mouseenter touchstart',
					function () {
						qodefButton.changeColor( $button, 'border-color', hoverBorderColor );
					}
				);
				$button.on(
					'mouseleave touchend',
					function () {
						qodefButton.changeColor( $button, 'border-color', originalBorderColor );
					}
				);
			}
		},
		changeColor: function ( $button, cssProperty, color ) {
			$button.css( cssProperty, color );
		}
	};

	qodefCore.shortcodes.luxedrive_core_button.qodefButton = qodefButton;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_countdown = {};

	$( document ).ready(
		function () {
			qodefCountdown.init();
		}
	);

	var qodefCountdown = {
		init: function () {
			this.countdowns = $( '.qodef-countdown' );

			if ( this.countdowns.length ) {
				this.countdowns.each(
					function () {
						qodefCountdown.initItem( $( this ) );
					}
				);
			}
		},
		initItem: function ( $currentItem ) {
			var $countdownElement = $currentItem.find( '.qodef-m-date' ),
				dateFormats       = ['week', 'day', 'hour', 'minute', 'second'],
				options           = qodefCountdown.generateOptions( $currentItem, dateFormats );

			qodefCountdown.initCountdown( $countdownElement, options, dateFormats );
		},
		generateOptions: function ( $countdown, dateFormats ) {
			var options = {};

			options.date = typeof $countdown.data( 'date' ) !== 'undefined' ? $countdown.data( 'date' ) : null;

			for ( var i = 0; i < dateFormats.length; i++ ) {
				var label       = dateFormats[i] + 'Label',
					labelPlural = dateFormats[i] + 'LabelPlural';

				options[label]       = typeof $countdown.data( dateFormats[i] + '-label' ) !== 'undefined' ? $countdown.data( dateFormats[i] + '-label' ) : '';
				options[labelPlural] = typeof $countdown.data( dateFormats[i] + '-label-plural' ) !== 'undefined' ? $countdown.data( dateFormats[i] + '-label-plural' ) : '';
			}

			return options;
		},
		initCountdown: function ( $countdownElement, options, dateFormats ) {
			var countDownDate = new Date( options.date ).getTime();

			// Update the count down every 1 second
			var x = setInterval(
				function () {

					// Get today's date and time
					var now = new Date().getTime();

					// Find the distance between now and the count down date
					var distance = countDownDate - now;

					// Time calculations for days, hours, minutes and seconds
					this.weeks   = Math.floor( distance / (1000 * 60 * 60 * 24 * 7) );
					this.days    = Math.floor( (distance % (1000 * 60 * 60 * 24 * 7)) / (1000 * 60 * 60 * 24) );
					this.hours   = Math.floor( (distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60) );
					this.minutes = Math.floor( (distance % (1000 * 60 * 60)) / (1000 * 60) );
					this.seconds = Math.floor( (distance % (1000 * 60)) / 1000 );

					for ( var i = 0; i < dateFormats.length; i++ ) {
						var dateName = dateFormats[i] + 's';
						qodefCountdown.initiateDate( $countdownElement, this[dateName], dateFormats[i], options );
					}

					// If the count down is finished, write some text
					if ( distance < 0 ) {
						clearInterval( x );
						qodefCountdown.afterClearInterval( $countdownElement, dateFormats, options );
					}
				},
				1000
			);
		},
		initiateDate: function ( $countdownElement, date, dateFormat, options ) {
			var $holder = $countdownElement.find( '.qodef-' + dateFormat + 's' );

			$holder.find( '.qodef-label' ).html( ( 1 === date ) ? options[dateFormat + 'Label'] : options[dateFormat + 'LabelPlural'] );

			date = (date < 10) ? '0' + date : date;

			$holder.find( '.qodef-digit' ).html( date );
		},
		afterClearInterval: function( $countdownElement, dateFormats, options ) {
			for ( var i = 0; i < dateFormats.length; i++ ) {
				var $holder = $countdownElement.find( '.qodef-' + dateFormats[i] + 's' );

				$holder.find( '.qodef-label' ).html( options[dateFormats[i] + 'LabelPlural'] );
				$holder.find( '.qodef-digit' ).html( '00' );
			}
		}
	};

	qodefCore.shortcodes.luxedrive_core_countdown.qodefCountdown = qodefCountdown;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_counter = {};

	$( document ).ready(
		function () {
			qodefCounter.init();
		}
	);

	var qodefCounter = {
		init: function () {
			this.counters = $( '.qodef-counter' );

			if ( this.counters.length ) {
				this.counters.each(
					function () {
						qodefCounter.initItem( $( this ) );
					}
				);
			}
		},
		initItem: function ( $currentItem ) {
			var $counterElement = $currentItem.find( '.qodef-m-digit' ),
				options         = qodefCounter.generateOptions( $currentItem );

			qodefCore.qodefIsInViewport.check(
				$currentItem,
				function () {
					qodefCounter.counterScript(
						$counterElement,
						options
					);
				}
			);
		},
		generateOptions: function ( $counter ) {
			var options = {};
			options.start = typeof $counter.data( 'start-digit' ) !== 'undefined' && $counter.data( 'start-digit' ) !== '' ? $counter.data( 'start-digit' ) : 0;
			options.end = typeof $counter.data( 'end-digit' ) !== 'undefined' && $counter.data( 'end-digit' ) !== '' ? $counter.data( 'end-digit' ) : null;
			options.step = typeof $counter.data( 'step-digit' ) !== 'undefined' && $counter.data( 'step-digit' ) !== '' ? $counter.data( 'step-digit' ) : 1;
			options.delay = typeof $counter.data( 'step-delay' ) !== 'undefined' && $counter.data( 'step-delay' ) !== '' ? parseInt(
				$counter.data( 'step-delay' ),
				10
			) : 100;
			options.txt = typeof $counter.data( 'digit-label' ) !== 'undefined' && $counter.data( 'digit-label' ) !== '' ? $counter.data( 'digit-label' ) : '';

			return options;
		},
		counterScript: function ( $counterElement, options ) {
			var defaults = {
				start: 0,
				end: null,
				step: 1,
				delay: 50,
				txt: '',
			};

			var settings = $.extend(
				defaults,
				options || {}
			);
			var nb_start = settings.start;
			var nb_end   = settings.end;

			$counterElement.text( nb_start ).append( '<span class="qodef-digit-label">' + settings.txt + '</span>' );

			// Timer
			// Launches every "settings.delay"
			var counterInterval = setInterval(
				function () {
					// Definition of conditions of arrest
					if ( nb_end !== null && nb_start >= nb_end ) {
						return;
					}

					// incrementation
					nb_start = nb_start + settings.step;

					// Check is ended
					if ( nb_start >= nb_end ) {
						nb_start = nb_end;

						clearInterval( counterInterval );
					}

					// display
					$counterElement.text( nb_start ).append( '<span class="qodef-digit-label">' + settings.txt + '</span>' );
				},
				settings.delay
			);
		}
	};

	qodefCore.shortcodes.luxedrive_core_counter.qodefCounter = qodefCounter;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_google_map = {};

	$( document ).on(
		'qodefGoogleMapsCallbackEvent',
		function () {
			qodefGoogleMap.init();
		}
	);

	var qodefGoogleMap = {
		init: function () {
			this.holder = $( '.qodef-google-map' );

			if ( this.holder.length ) {
				this.holder.each(
					function () {
						qodefGoogleMap.initItem( $( this ) );
					}
				);
			}
		},
		initItem: function ( $currentItem ) {
			if ( typeof window.qodefGoogleMap !== 'undefined' ) {
				window.qodefGoogleMap.init( $currentItem.find( '.qodef-m-map' ) );
			}
		},
	};

	qodefCore.shortcodes.luxedrive_core_google_map.qodefGoogleMap = qodefGoogleMap;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_icon = {};

	$( document ).ready(
		function () {
			qodefIcon.init();
		}
	);

	var qodefIcon = {
		init: function () {
			this.icons = $( '.qodef-icon-holder' );

			if ( this.icons.length ) {
				this.icons.each(
					function () {
						qodefIcon.initItem( $( this ) );
					}
				);
			}
		},
		initItem: function ( $currentItem ) {
			qodefIcon.iconHoverColor( $currentItem );
			qodefIcon.iconHoverBgColor( $currentItem );
			qodefIcon.iconHoverBorderColor( $currentItem );
		},
		iconHoverColor: function ( $iconHolder ) {
			if ( typeof $iconHolder.data( 'hover-color' ) !== 'undefined' ) {
				var spanHolder    = $iconHolder.find( 'span' ).length ? $iconHolder.find( 'span' ) : $iconHolder;
				var originalColor = spanHolder.css( 'color' );
				var hoverColor    = $iconHolder.data( 'hover-color' );

				$iconHolder.on(
					'mouseenter',
					function () {
						qodefIcon.changeColor(
							spanHolder,
							'color',
							hoverColor
						);
					}
				);
				$iconHolder.on(
					'mouseleave',
					function () {
						qodefIcon.changeColor(
							spanHolder,
							'color',
							originalColor
						);
					}
				);
			}
		},
		iconHoverBgColor: function ( $iconHolder ) {
			if ( typeof $iconHolder.data( 'hover-background-color' ) !== 'undefined' ) {
				var hoverBackgroundColor    = $iconHolder.data( 'hover-background-color' );
				var originalBackgroundColor = $iconHolder.css( 'background-color' );

				$iconHolder.on(
					'mouseenter',
					function () {
						qodefIcon.changeColor(
							$iconHolder,
							'background-color',
							hoverBackgroundColor
						);
					}
				);
				$iconHolder.on(
					'mouseleave',
					function () {
						qodefIcon.changeColor(
							$iconHolder,
							'background-color',
							originalBackgroundColor
						);
					}
				);
			}
		},
		iconHoverBorderColor: function ( $iconHolder ) {
			if ( typeof $iconHolder.data( 'hover-border-color' ) !== 'undefined' ) {
				var hoverBorderColor    = $iconHolder.data( 'hover-border-color' );
				var originalBorderColor = $iconHolder.css( 'borderTopColor' );

				$iconHolder.on(
					'mouseenter',
					function () {
						qodefIcon.changeColor(
							$iconHolder,
							'border-color',
							hoverBorderColor
						);
					}
				);
				$iconHolder.on(
					'mouseleave',
					function () {
						qodefIcon.changeColor(
							$iconHolder,
							'border-color',
							originalBorderColor
						);
					}
				);
			}
		},
		changeColor: function ( iconElement, cssProperty, color ) {
			iconElement.css(
				cssProperty,
				color
			);
		}
	};

	qodefCore.shortcodes.luxedrive_core_icon.qodefIcon = qodefIcon;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_icon_with_text = {};

	$( document ).ready(
		function () {
			qodefIconWithText.init();
		}
	);

	var qodefIconWithText = {
		init: function () {
			this.iconText = $( '.qodef-icon-with-text .qodef-m-title, .qodef-icon-with-text .qodef-m-text' );

			if ( this.iconText.length ) {
				this.iconText.each(
					function () {
						qodefIconWithText.initItem( $( this ) );
					}
				);
			}
		},
		initItem: function ( $currentItem ) {
			qodefIconWithText.hoverColor( $currentItem );
		},
		hoverColor: function ( $button ) {
			if ( typeof $button.data( 'hover-color' ) !== 'undefined' ) {
				var hoverColor    = $button.data( 'hover-color' );
				var originalColor = $button.css( 'color' );

				$button.on(
					'mouseenter touchstart',
					function () {
						qodefIconWithText.changeColor( $button, 'color', hoverColor );
					}
				);
				$button.on(
					'mouseleave touchend',
					function () {
						qodefIconWithText.changeColor( $button, 'color', originalColor );
					}
				);
			}
		},
		changeColor: function ( $button, cssProperty, color ) {
			$button.css( cssProperty, color );
		}
	};

	qodefCore.shortcodes.luxedrive_core_icon_with_text.qodefIconWithText = qodefIconWithText;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_image_gallery                    = {};
	qodefCore.shortcodes.luxedrive_core_image_gallery.qodefSwiper        = qodef.qodefSwiper;
	qodefCore.shortcodes.luxedrive_core_image_gallery.qodefMasonryLayout = qodef.qodefMasonryLayout;
	qodefCore.shortcodes.luxedrive_core_image_gallery.qodefMagnificPopup = qodef.qodefMagnificPopup;
	qodefCore.shortcodes.luxedrive_core_image_gallery.qodefCustomCursor  = qodefCore.qodefCustomCursor;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_image_with_text                    = {};
	qodefCore.shortcodes.luxedrive_core_image_with_text.qodefMagnificPopup = qodef.qodefMagnificPopup;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_pricing_table = {};

	$( document ).ready(
		function () {
			qodefPricingTable.init();
		}
	);

	/**
	 * Init progress bar shortcode functionality
	 */
	var qodefPricingTable = {
		init: function () {
			this.holder = $( '.qodef-pricing-table.qodef-has-appear' );

			if ( this.holder.length ) {
				this.holder.each(
					function () {
						qodefPricingTable.initItem( $( this ) );
					}
				);
			}
		},
		initItem: function ( $currentItem ) {

			qodef.qodefWaitForImages.check(
				$currentItem,
				function () {
					qodefCore.qodefIsInViewport.check(
						$currentItem,
						function () {
							$currentItem.addClass( 'qodef--appeared' );
						}
					);
				}
			);
		}
	};

	qodefCore.shortcodes.luxedrive_core_pricing_table.qodefPricingTable = qodefPricingTable;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_progress_bar = {};

	$( document ).ready(
		function () {
			qodefProgressBar.init();
		}
	);

	/**
	 * Init progress bar shortcode functionality
	 */
	var qodefProgressBar = {
		init: function () {
			this.holder = $( '.qodef-progress-bar' );

			if ( this.holder.length ) {
				this.holder.each(
					function () {
						qodefProgressBar.initItem( $( this ) );
					}
				);
			}
		},
		initItem: function ( $currentItem ) {
			var layout = $currentItem.data( 'layout' );

			qodefCore.qodefIsInViewport.check(
				$currentItem,
				function () {
					$currentItem.addClass( 'qodef--init' );

					var $container = $currentItem.find( '.qodef-m-canvas' ),
						data       = qodefProgressBar.generateBarData(
							$currentItem,
							layout
						),
						number     = $currentItem.data( 'number' ) / 100;

					switch (layout) {
						case 'circle':
							qodefProgressBar.initCircleBar(
								$container,
								data,
								number
							);
							break;
						case 'semi-circle':
							qodefProgressBar.initSemiCircleBar(
								$container,
								data,
								number
							);
							break;
						case 'line':
							data = qodefProgressBar.generateLineData(
								$currentItem,
								number
							);
							qodefProgressBar.initLineBar(
								$container,
								data
							);
							break;
						case 'custom':
							qodefProgressBar.initCustomBar(
								$container,
								data,
								number
							);
							break;
					}
				}
			);
		},
		generateBarData: function ( thisBar, layout ) {
			var activeWidth   = thisBar.data( 'active-line-width' );
			var activeColor   = thisBar.data( 'active-line-color' );
			var inactiveWidth = thisBar.data( 'inactive-line-width' );
			var inactiveColor = thisBar.data( 'inactive-line-color' );
			var easing        = 'linear';
			var duration      = typeof thisBar.data( 'duration' ) !== 'undefined' && thisBar.data( 'duration' ) !== '' ? parseInt(
				thisBar.data( 'duration' ),
				10
			) : 1600;
			var textColor     = thisBar.data( 'text-color' );

			return {
				strokeWidth: activeWidth,
				color: activeColor,
				trailWidth: inactiveWidth,
				trailColor: inactiveColor,
				easing: easing,
				duration: duration,
				svgStyle: {
					width: '100%',
					height: '100%'
				},
				text: {
					style: {
						color: textColor
					},
					autoStyleContainer: false
				},
				from: {
					color: inactiveColor
				},
				to: {
					color: activeColor
				},
				step: function ( state, bar ) {
					if ( layout !== 'custom' ) {
						bar.setText( Math.round( bar.value() * 100 ) + '%' );
					}
				},
			};
		},
		generateLineData: function ( thisBar, number ) {
			var height         = thisBar.data( 'active-line-width' );
			var activeColor    = thisBar.data( 'active-line-color' );
			var inactiveHeight = thisBar.data( 'inactive-line-width' );
			var inactiveColor  = thisBar.data( 'inactive-line-color' );
			var duration       = typeof thisBar.data( 'duration' ) !== 'undefined' && thisBar.data( 'duration' ) !== '' ? parseInt(
				thisBar.data( 'duration' ),
				10
			) : 1600;
			var textColor      = thisBar.data( 'text-color' );

			return {
				percentage: number * 100,
				duration: duration,
				fillBackgroundColor: activeColor,
				backgroundColor: inactiveColor,
				height: height,
				inactiveHeight: inactiveHeight,
				followText: thisBar.hasClass( 'qodef-percentage--floating' ),
				textColor: textColor,
			};
		},
		initCircleBar: function ( $container, data, number ) {
			if ( qodefProgressBar.checkBar( $container ) ) {
				var $bar = new ProgressBar.Circle(
					$container[0],
					data
				);

				$bar.animate( number );
			}
		},
		initSemiCircleBar: function ( $container, data, number ) {
			if ( qodefProgressBar.checkBar( $container ) ) {
				var $bar = new ProgressBar.SemiCircle(
					$container[0],
					data
				);

				$bar.animate( number );
			}
		},
		initCustomBar: function ( $container, data, number ) {
			if ( qodefProgressBar.checkBar( $container ) ) {
				var $bar = new ProgressBar.Path(
					$container[0],
					data
				);

				$bar.set( 0 );
				$bar.animate( number );
			}
		},
		initLineBar: function ( $container, data ) {
			$container.LineProgressbar( data );
		},
		checkBar: function ( $container ) {
			// check if svg is already in container, elementor fix
			return ! $container.find( 'svg' ).length;
		}
	};

	qodefCore.shortcodes.luxedrive_core_progress_bar.qodefProgressBar = qodefProgressBar;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_separator = {};

	$( document ).ready(
		function () {
			qodefSeparator.init();
		}
	);

	/**
	 * Init progress bar shortcode functionality
	 */
	var qodefSeparator = {
		init: function () {
			this.holder = $( '.qodef-separator' );

			if ( this.holder.length ) {
				this.holder.each(
					function () {
						qodefSeparator.initItem( $( this ) );
					}
				);
			}
		},
		initItem: function ( $currentItem ) {

			qodefCore.qodefIsInViewport.check(
				$currentItem,
				function () {
					$currentItem.addClass( 'qodef--appeared' );
				}
			);
		}
	};

	qodefCore.shortcodes.luxedrive_core_separator.qodefSeparator = qodefSeparator;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_single_image = {};

	$( document ).ready(
		function () {
			qodefSingleImage.init();
		}
	);

	/**
	 * Init progress bar shortcode functionality
	 */
	var qodefSingleImage = {
		init: function () {
			this.holder = $( '.qodef-single-image.qodef-has-appear' );

			if ( this.holder.length ) {
				this.holder.each(
					function () {
						qodefSingleImage.initItem( $( this ) );
					}
				);
			}
		},
		initItem: function ( $currentItem ) {

			qodef.qodefWaitForImages.check(
				$currentItem,
				function () {
					qodefCore.qodefIsInViewport.check(
						$currentItem,
						function () {
							$currentItem.addClass( 'qodef--appeared' );
						}
					);
				}
			);
		}
	};

	qodefCore.shortcodes.luxedrive_core_single_image.qodefSingleImage = qodefSingleImage;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_tabs = {};

	$( document ).ready(
		function () {
			qodefTabs.init();
		}
	);

	var qodefTabs = {
		init: function () {
			this.holder = $( '.qodef-tabs' );

			if ( this.holder.length ) {
				this.holder.each(
					function () {
						qodefTabs.initItem( $( this ) );
					}
				);
			}
		},
		initItem: function ( $currentItem ) {
			$currentItem.children( '.qodef-tabs-content' ).each(
				function ( index ) {
					index = index + 1;

					var $that    = $( this ),
						link     = $that.attr( 'id' ),
						$navItem = $that.parent().find( '.qodef-tabs-navigation li:nth-child(' + index + ') a' ),
						navLink  = $navItem.attr( 'href' );

					link = '#' + link;

					if ( link.indexOf( navLink ) > -1 ) {
						$navItem.attr(
							'href',
							link
						);
					}
				}
			);

			$currentItem.addClass( 'qodef--init' ).tabs();
		},
		setHeight ( $holder ) {
			var $navigation      = $holder.find( '.qodef-tabs-navigation' ),
				$content         = $holder.find( '.qodef-tabs-content' ),
				navHeight,
				contentHeight,
				maxContentHeight = 0;

			if ( $navigation.length ) {
				navHeight = $navigation.outerHeight( true );
			}

			if ( $content.length ) {
				$content.each(
					function () {
						contentHeight = $( this ).outerHeight( true );
						maxContentHeight = contentHeight > maxContentHeight ? contentHeight : maxContentHeight;
					}
				)
			}

			$holder.height(navHeight + maxContentHeight);
		}
	};

	qodefCore.shortcodes.luxedrive_core_tabs.qodefTabs = qodefTabs;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_video_button = {};
	
	$( document ).ready(
		function () {
			qodefVideoButton.init();
		}
	);
	
	var qodefVideoButton = {
		init: function () {
			this.holder = $( '.qodef-video-button' );
			
			if ( this.holder.length ) {
				this.holder.each(
					function () {
						qodefVideoButton.initItem( $( this ) );
					}
				);
			}
		},
		initItem: function ( $currentItem ) {
			var bodyClasses = $('body').attr('class'),
				height = $currentItem.find('.qodef-m-image img').height() > 300 ? $currentItem.find('.qodef-m-image img').height() : 300,
				padHeight = $currentItem.find('.qodef-m-image img').height() > 314 ? $currentItem.find('.qodef-m-image img').height() : 314,
				gridClassArray = bodyClasses.split(' '),
				gridClass = $.makeArray( gridClassArray ).filter( current => current.startsWith('qodef-content-grid-') );
			
			gridClass = gridClass[0].replace('qodef-content-grid-', '');
			
			if ( gridClass && gridClassArray.includes('page-template-page-full-width') && ! $currentItem.closest('.elementor-section').hasClass('qodef-elementor-content-grid') ) {
				$currentItem.find('.qodef-m-play').wrap('<div class="qodef-content-grid"><div class="qodef-e-content"></div></div>');
				$currentItem.addClass('qodef-background-image')
			}
			
			if ( qodef.windowWidth >= 768 ) {
				$currentItem.find('.qodef-content-grid').height( padHeight );
			} else {
				$currentItem.find('.qodef-content-grid').height( height );
			}
		}
	};
	
	qodefCore.shortcodes.luxedrive_core_video_button.qodefMagnificPopup = qodef.qodefMagnificPopup;
	qodefCore.shortcodes.luxedrive_core_video_button.qodefMagnificPopup = qodef.qodefMagnificPopup;

})( jQuery );

(function ( $ ) {
	'use strict';

	$( window ).on(
		'load',
		function () {
			qodefStickySidebar.init();
		}
	);

	var qodefStickySidebar = {
		init: function () {
			var info = $( '.widget_luxedrive_core_sticky_sidebar' );

			if ( info.length && qodefCore.windowWidth > 1024 ) {
				info.wrapper = info.parents( '#qodef-page-sidebar' );
				info.offsetM = info.offset().top - info.wrapper.offset().top;
				info.adj     = 15;

				qodefStickySidebar.callStack( info );

				$( window ).on(
					'resize',
					function () {
						if ( qodefCore.windowWidth > 1024 ) {
							qodefStickySidebar.callStack( info );
						}
					}
				);

				$( window ).on(
					'scroll',
					function () {
						if ( qodefCore.windowWidth > 1024 ) {
							qodefStickySidebar.infoPosition( info );
						}
					}
				);
			}
		},
		calc: function ( info ) {
			var content = $( '.qodef-page-content-section' ),
				headerH = qodefCore.body.hasClass( 'qodef-header-appearance--none' ) ? 0 : parseInt( qodefGlobal.vars.headerHeight, 10 );

			// If posts not found set content to have the same height as the sidebar
			if ( qodefCore.windowWidth > 1024 && content.height() < 100 ) {
				content.css( 'height', info.wrapper.height() - content.height() );
			}

			info.start = content.offset().top;
			info.end   = content.outerHeight();
			info.h     = info.wrapper.height();
			info.w     = info.outerWidth();
			info.left  = info.offset().left;
			info.top   = headerH + qodefGlobal.vars.adminBarHeight - info.offsetM;
			info.data( 'state', 'top' );
		},
		infoPosition: function ( info ) {
			if ( qodefCore.scroll < info.start - info.top && qodefCore.scroll + info.h && info.data( 'state' ) !== 'top' ) {
				gsap.to(
					info.wrapper,
					.1,
					{
						y: 5,
					}
				);
				gsap.to(
					info.wrapper,
					.3,
					{
						y: 0,
						delay: .1,
					}
				);
				info.data( 'state', 'top' );
				info.wrapper.css(
					{
						'position': 'static',
					}
				);
			} else if ( qodefCore.scroll >= info.start - info.top && qodefCore.scroll + info.h + info.adj <= info.start + info.end &&
				info.data( 'state' ) !== 'fixed' ) {
				var c = info.data( 'state' ) === 'top' ? 1 : -1;
				info.data( 'state', 'fixed' );
				info.wrapper.css(
					{
						'position': 'fixed',
						'top': info.top,
						'left': info.left,
						'width': info.w,
					}
				);
				gsap.fromTo(
					info.wrapper,
					.2,
					{
						y: 0
					},
					{
						y: c * 10,
						ease: Power4.easeInOut
					}
				);
				gsap.to(
					info.wrapper,
					.2,
					{
						y: 0,
						delay: .2,
					}
				);
			} else if ( qodefCore.scroll + info.h + info.adj > info.start + info.end && info.data( 'state' ) !== 'bottom' ) {
				info.data( 'state', 'bottom' );
				info.wrapper.css(
					{
						'position': 'absolute',
						'top': info.end - info.h - info.adj,
						'left': 'auto',
						'width': info.w,
					}
				);
				gsap.fromTo(
					info.wrapper,
					.1,
					{
						y: 0
					},
					{
						y: -5,
					}
				);
				gsap.to(
					info.wrapper,
					.3,
					{
						y: 0,
						delay: .1,
					}
				);
			}
		},
		callStack: function ( info ) {
			this.calc( info );
			this.infoPosition( info );
		}
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	var shortcode = 'luxedrive_core_blog_list';

	qodefCore.shortcodes[shortcode] = {};

	if ( typeof qodefCore.listShortcodesScripts === 'object' ) {
		$.each(
			qodefCore.listShortcodesScripts,
			function ( key, value ) {
				qodefCore.shortcodes[shortcode][key] = value;
			}
		);
	}

	qodefCore.shortcodes[shortcode].qodefResizeIframes = qodef.qodefResizeIframes;

	$( window ).on(
		'load',
		function () {
			qodefBlogList.init();
		}
	);

	$( document ).on(
		'luxedrive_trigger_get_new_posts',
		function () {
			qodefBlogList.init();
		}
	);

	var qodefBlogList = {
		init: function () {
			this.holder = $( '.qodef-shortcode.qodef-blog' );

			if ( this.holder.length ) {
				this.holder.each(
					function () {
						qodefBlogList.initHover( $( this ) );
					}
				);
			}
		},
		initHover: function ( $currentList ) {
			var $items = $currentList.find( '.qodef-e' );

			if ( $items.length ) {
				$items.each(
					function () {
						var $item  = $( this );
						var $links = $item.find( '.qodef-e-media-image a, .qodef-e-title-link, .qodef-button' );

						$links.on(
							'mouseenter',
							function () {
								$item.addClass( 'qodef--hover' );
							}
						).on(
							'mouseleave',
							function () {
								$item.removeClass( 'qodef--hover' );
							}
						);
					}
				);
			}
		},
	};

	qodefCore.shortcodes.luxedrive_core_blog_list.qodefBlogList = qodefBlogList;

})( jQuery );

(function ( $ ) {
	'use strict';

	var fixedHeaderAppearance = {
		showHideHeader: function ( $pageOuter, $header ) {
			if ( qodefCore.windowWidth > 1024 ) {
				if ( qodefCore.scroll <= 0 ) {
					qodefCore.body.removeClass( 'qodef-header--fixed-display' );
					$pageOuter.css( 'padding-top', '0' );
					$header.css( 'margin-top', '0' );
				} else {
					qodefCore.body.addClass( 'qodef-header--fixed-display' );
					$pageOuter.css( 'padding-top', parseInt( qodefGlobal.vars.headerHeight + qodefGlobal.vars.topAreaHeight ) + 'px' );
					$header.css( 'margin-top', parseInt( qodefGlobal.vars.topAreaHeight ) + 'px' );
				}
			}
		},
		init: function () {

			if ( ! qodefCore.body.hasClass( 'qodef-header--vertical' ) ) {
				var $pageOuter = $( '#qodef-page-outer' ),
					$header    = $( '#qodef-page-header' );

				fixedHeaderAppearance.showHideHeader( $pageOuter, $header );

				$( window ).scroll(
					function () {
						fixedHeaderAppearance.showHideHeader( $pageOuter, $header );
					}
				);

				$( window ).resize(
					function () {
						$pageOuter.css( 'padding-top', '0' );
						fixedHeaderAppearance.showHideHeader( $pageOuter, $header );
					}
				);
			}
		}
	};

	qodefCore.fixedHeaderAppearance = fixedHeaderAppearance.init;

})( jQuery );

(function ( $ ) {
	'use strict';

	var stickyHeaderAppearance = {
		header: '',
		docYScroll: 0,
		init: function () {
			var displayAmount = stickyHeaderAppearance.displayAmount();

			// Set variables
			stickyHeaderAppearance.header 	  = $( '.qodef-header-sticky' );
			stickyHeaderAppearance.docYScroll = $( document ).scrollTop();

			// Set sticky visibility
			stickyHeaderAppearance.setVisibility( displayAmount );

			$( window ).scroll(
				function () {
					stickyHeaderAppearance.setVisibility( displayAmount );
				}
			);
		},
		displayAmount: function () {
			if ( qodefGlobal.vars.qodefStickyHeaderScrollAmount !== 0 ) {
				return parseInt( qodefGlobal.vars.qodefStickyHeaderScrollAmount, 10 );
			} else {
				return parseInt( qodefGlobal.vars.headerHeight + qodefGlobal.vars.adminBarHeight, 10 );
			}
		},
		setVisibility: function ( displayAmount ) {
			var isStickyHidden = qodefCore.scroll < displayAmount;

			if ( stickyHeaderAppearance.header.hasClass( 'qodef-appearance--up' ) ) {
				var currentDocYScroll = $( document ).scrollTop();

				isStickyHidden = (currentDocYScroll > stickyHeaderAppearance.docYScroll && currentDocYScroll > displayAmount) || (currentDocYScroll < displayAmount);

				stickyHeaderAppearance.docYScroll = $( document ).scrollTop();
			}

			stickyHeaderAppearance.showHideHeader( isStickyHidden );
		},
		showHideHeader: function ( isStickyHidden ) {
			if ( isStickyHidden ) {
				qodefCore.body.removeClass( 'qodef-header--sticky-display' );
			} else {
				qodefCore.body.addClass( 'qodef-header--sticky-display' );
			}
		},
	};

	qodefCore.stickyHeaderAppearance = stickyHeaderAppearance.init;

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function () {
			qodefSideAreaMobileHeader.init();
		}
	);

	var qodefSideAreaMobileHeader = {
		init: function () {
			var $holder = $( '#qodef-side-area-mobile-header' );

			if ( $holder.length && qodefCore.body.hasClass( 'qodef-mobile-header--side-area' ) ) {
				var $navigation = $holder.find( '.qodef-m-navigation' );

				qodefSideAreaMobileHeader.initOpenerTrigger( $holder, $navigation );
				qodefSideAreaMobileHeader.initNavigationClickToggle( $navigation );

				if ( typeof qodefCore.qodefPerfectScrollbar === 'object' ) {
					qodefCore.qodefPerfectScrollbar.init( $holder );
				}
			}
		},
		initOpenerTrigger: function ( $holder, $navigation ) {
			var $openerIcon = $( '.qodef-side-area-mobile-header-opener' ),
				$closeIcon  = $holder.children( '.qodef-m-close' );

			if ( $openerIcon.length && $navigation.length ) {
				$openerIcon.on(
					'tap click',
					function ( e ) {
						e.stopPropagation();
						e.preventDefault();

						if ( $holder.hasClass( 'qodef--opened' ) ) {
							$holder.removeClass( 'qodef--opened' );
						} else {
							$holder.addClass( 'qodef--opened' );
						}
					}
				);
			}

			$closeIcon.on(
				'tap click',
				function ( e ) {
					e.stopPropagation();
					e.preventDefault();

					if ( $holder.hasClass( 'qodef--opened' ) ) {
						$holder.removeClass( 'qodef--opened' );
					}
				}
			);
		},
		initNavigationClickToggle: function ( $navigation ) {
			var $menuItems = $navigation.find( 'ul li.menu-item-has-children' );

			$menuItems.each(
				function () {
					var $thisItem        = $( this ),
						$elementToExpand = $thisItem.find( ' > .qodef-drop-down-second, > ul' ),
						$dropdownOpener  = $thisItem.find( '> .qodef-menu-item-arrow' ),
						slideUpSpeed     = 'fast',
						slideDownSpeed   = 'slow';

					$dropdownOpener.on(
						'click tap',
						function ( e ) {
							e.preventDefault();
							e.stopPropagation();

							if ( $elementToExpand.is( ':visible' ) ) {
								$thisItem.removeClass( 'qodef-menu-item--open' );
								$elementToExpand.slideUp( slideUpSpeed );
							} else if ( $dropdownOpener.parent().parent().children().hasClass( 'qodef-menu-item--open' ) && $dropdownOpener.parent().parent().parent().hasClass( 'qodef-vertical-menu' ) ) {
								$thisItem.parent().parent().children().removeClass( 'qodef-menu-item--open' );
								$thisItem.parent().parent().children().find( ' > .qodef-drop-down-second' ).slideUp( slideUpSpeed );

								$thisItem.addClass( 'qodef-menu-item--open' );
								$elementToExpand.slideDown( slideDownSpeed );
							} else {

								if ( ! $thisItem.parents( 'li' ).hasClass( 'qodef-menu-item--open' ) ) {
									$menuItems.removeClass( 'qodef-menu-item--open' );
									$menuItems.find( ' > .qodef-drop-down-second, > ul' ).slideUp( slideUpSpeed );
								}

								if ( $thisItem.parent().parent().children().hasClass( 'qodef-menu-item--open' ) ) {
									$thisItem.parent().parent().children().removeClass( 'qodef-menu-item--open' );
									$thisItem.parent().parent().children().find( ' > .qodef-drop-down-second, > ul' ).slideUp( slideUpSpeed );
								}

								$thisItem.addClass( 'qodef-menu-item--open' );
								$elementToExpand.slideDown( slideDownSpeed );
							}
						}
					);
				}
			);
		},
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function () {
			qodefSearchCoversHeader.init();
		}
	);

	var qodefSearchCoversHeader = {
		init: function () {
			var $searchOpener = $( 'a.qodef-search-opener' ),
				$searchForm   = $( '.qodef-search-cover-form' ),
				$searchClose  = $searchForm.find( '.qodef-m-close' );

			if ( $searchOpener.length && $searchForm.length ) {
				$searchOpener.on(
					'click',
					function ( e ) {
						e.preventDefault();
						qodefSearchCoversHeader.openCoversHeader( $searchForm );
					}
				);
				$searchClose.on(
					'click',
					function ( e ) {
						e.preventDefault();
						qodefSearchCoversHeader.closeCoversHeader( $searchForm );
					}
				);
			}
		},
		openCoversHeader: function ( $searchForm ) {
			qodefCore.body.addClass( 'qodef-covers-search--opened qodef-covers-search--fadein' );
			qodefCore.body.removeClass( 'qodef-covers-search--fadeout' );

			setTimeout(
				function () {
					$searchForm.find( '.qodef-m-form-field' ).focus();
				},
				600
			);
		},
		closeCoversHeader: function ( $searchForm ) {
			qodefCore.body.removeClass( 'qodef-covers-search--opened qodef-covers-search--fadein' );
			qodefCore.body.addClass( 'qodef-covers-search--fadeout' );

			setTimeout(
				function () {
					$searchForm.find( '.qodef-m-form-field' ).val( '' );
					$searchForm.find( '.qodef-m-form-field' ).blur();
					qodefCore.body.removeClass( 'qodef-covers-search--fadeout' );
				},
				300
			);
		}
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function () {
			qodefSearchFullscreen.init();
		}
	);

	var qodefSearchFullscreen = {
		init: function () {
			var $searchOpener = $( 'a.qodef-search-opener' ),
				$searchHolder = $( '.qodef-fullscreen-search-holder' ),
				$searchClose  = $searchHolder.find( '.qodef-m-close' );

			if ( $searchOpener.length && $searchHolder.length ) {
				$searchOpener.on(
					'click',
					function ( e ) {
						e.preventDefault();
						if ( qodefCore.body.hasClass( 'qodef-fullscreen-search--opened' ) ) {
							qodefSearchFullscreen.closeFullscreen( $searchHolder );
						} else {
							qodefSearchFullscreen.openFullscreen( $searchHolder );
						}
					}
				);
				$searchClose.on(
					'click',
					function ( e ) {
						e.preventDefault();
						qodefSearchFullscreen.closeFullscreen( $searchHolder );
					}
				);

				//Close on escape
				$( document ).keyup(
					function ( e ) {
						if ( e.keyCode === 27 && qodefCore.body.hasClass( 'qodef-fullscreen-search--opened' ) ) { //KeyCode for ESC button is 27
							qodefSearchFullscreen.closeFullscreen( $searchHolder );
						}
					}
				);
			}
		},
		openFullscreen: function ( $searchHolder ) {
			qodefCore.body.removeClass( 'qodef-fullscreen-search--fadeout' );
			qodefCore.body.addClass( 'qodef-fullscreen-search--opened qodef-fullscreen-search--fadein' );

			var $searchClose = $searchHolder.find( '.qodef-m-close' ),
				$form        = $searchHolder.find( '.qodef-m-form' );

			qodefSearchFullscreen.initCloseCursor(
				$searchHolder,
				$searchClose,
				$form
			);

			setTimeout(
				function () {
					$searchHolder.find( '.qodef-m-form-field' ).focus();
				},
				900
			);

			qodefCore.qodefScroll.disable();
		},
		closeFullscreen: function ( $searchHolder ) {
			qodefCore.body.removeClass( 'qodef-fullscreen-search--opened qodef-fullscreen-search--fadein' );
			qodefCore.body.addClass( 'qodef-fullscreen-search--fadeout' );

			setTimeout(
				function () {
					$searchHolder.find( '.qodef-m-form-field' ).val( '' );
					$searchHolder.find( '.qodef-m-form-field' ).blur();
					qodefCore.body.removeClass( 'qodef-fullscreen-search--fadeout' );
				},
				300
			);

			qodefCore.qodefScroll.enable();
		},
		initCloseCursor: function ( $overlay, $cursor, $content ) {
			$overlay.on(
				'mouseenter',
				function () {
					$cursor.addClass( 'qodef--active' );
				}
			).on(
				'mouseleave',
				function () {
					$cursor.removeClass( 'qodef--active' );
				}
			);

			$( window ).on(
				'mousemove',
				function ( e ) {
					if ( $cursor.hasClass( 'qodef--active' ) ) {
						var x      = e.clientX,
							y      = e.clientY,
							deltaY = $cursor.height() / 2,
							deltaX = $cursor.width() / 2;

						$cursor.css( {
							'top': y - deltaY,
							'left': x - deltaX
						} );
					}
				}
			);

			$content.on(
				'mouseenter',
				function () {
					$cursor.removeClass( 'qodef--active' );
				}
			).on(
				'mouseleave',
				function () {
					$cursor.addClass( 'qodef--active' );
				}
			);
		},
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function () {
			qodefSearch.init();
		}
	);

	var qodefSearch = {
		init: function () {
			this.search = $( 'a.qodef-search-opener' );

			if ( this.search.length ) {
				this.search.each(
					function () {
						var $thisSearch = $( this );

						qodefSearch.searchHoverColor( $thisSearch );
					}
				);
			}
		},
		searchHoverColor: function ( $searchHolder ) {
			if ( typeof $searchHolder.data( 'hover-color' ) !== 'undefined' ) {
				var hoverColor    = $searchHolder.data( 'hover-color' ),
					originalColor = $searchHolder.css( 'color' );

				$searchHolder.on(
					'mouseenter',
					function () {
						$searchHolder.css( 'color', hoverColor );
					}
				).on(
					'mouseleave',
					function () {
						$searchHolder.css( 'color', originalColor );
					}
				);
			}
		}
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function() {
			qodefProgressBarSpinner.init();
		}
	);

	$( window ).on(
		'load',
		function () {
			qodefProgressBarSpinner.windowLoaded = true;
			qodefProgressBarSpinner.completeAnimation();
		}
	);

	$( window ).on(
		'elementor/frontend/init',
		function () {
			var isEditMode = Boolean( elementorFrontend.isEditMode() );

			if ( isEditMode ) {
				qodefProgressBarSpinner.init( isEditMode );
			}
		}
	);

	var qodefProgressBarSpinner = {
		holder: '',
		windowLoaded: false,
		percentNumber: 0,
		init: function ( isEditMode ) {
			this.holder = $( '#qodef-page-spinner.qodef-layout--progress-bar' );

			if ( this.holder.length ) {
				qodefProgressBarSpinner.animateSpinner( this.holder, isEditMode );
			}
		},
		animateSpinner: function ( $holder, isEditMode ) {
			var $numberHolder = $holder.find( '.qodef-m-spinner-number-label' ),
				$spinnerLine  = $holder.find( '.qodef-m-spinner-line-front' );

			$spinnerLine.animate(
				{ 'width': '100%' },
				10000,
				'linear'
			);

			var numberInterval = setInterval(
				function () {
					qodefProgressBarSpinner.animatePercent( $numberHolder, qodefProgressBarSpinner.percentNumber );

					if ( qodefProgressBarSpinner.windowLoaded ) {
						clearInterval( numberInterval );
					}
				},
				100
			);

			if ( isEditMode ) {
				qodefProgressBarSpinner.fadeOutLoader( $holder );
			}
		},
		completeAnimation: function () {
			var $holder = qodefProgressBarSpinner.holder.length ? qodefProgressBarSpinner.holder : $( '#qodef-page-spinner.qodef-layout--progress-bar' );

			var numberIntervalFastest = setInterval(
				function () {

					if ( qodefProgressBarSpinner.percentNumber >= 100 ) {
						clearInterval( numberIntervalFastest );

						$holder.find( '.qodef-m-spinner-line-front' ).stop().animate(
							{ 'width': '100%' },
							500
						);

						$holder.addClass( 'qodef--finished' );

						setTimeout(
							function () {
								qodefProgressBarSpinner.fadeOutLoader( $holder );
							},
							600
						);
					} else {
						qodefProgressBarSpinner.animatePercent(
							$holder.find( '.qodef-m-spinner-number-label' ),
							qodefProgressBarSpinner.percentNumber
						);
					}
				},
				6
			);
		},
		animatePercent: function ( $numberHolder, percentNumber ) {
			if ( percentNumber < 100 ) {
				percentNumber += 5;
				$numberHolder.text( percentNumber );

				qodefProgressBarSpinner.percentNumber = percentNumber;
			}
		},
		fadeOutLoader: function ( $holder, speed, delay, easing ) {
			speed  = speed ? speed : 600;
			delay  = delay ? delay : 0;
			easing = easing ? easing : 'swing';

			$holder.delay( delay ).fadeOut( speed, easing );

			$( window ).on(
				'bind',
				'pageshow',
				function ( event ) {
					if ( event.originalEvent.persisted ) {
						$holder.fadeOut( speed, easing );
					}
				}
			);
		}
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function () {
			qodefTextualSpinner.init();
		}
	);

	$( window ).on(
		'load',
		function () {
			qodefTextualSpinner.windowLoaded = true;
		}
	);

	$( window ).on(
		'elementor/frontend/init',
		function () {
			var isEditMode = Boolean( elementorFrontend.isEditMode() );

			if ( isEditMode ) {
				qodefTextualSpinner.init( isEditMode );
			}
		}
	);

	var qodefTextualSpinner = {
		init ( isEditMode ) {
			var $holder = $( '#qodef-page-spinner.qodef-layout--textual' );

			if ( $holder.length ) {
				if ( isEditMode ) {
					qodefTextualSpinner.fadeOutLoader( $holder );
				} else {
					qodefTextualSpinner.splitText( $holder );
				}
			}
		},
		splitText ( $holder ) {
			var $textHolder = $holder.find( '.qodef-m-text' );

			if ( $textHolder.length ) {
				var text     = $textHolder.text().trim(),
					chars    = text.split( '' ),
					cssClass = '';

				$textHolder.empty();

				chars.forEach(
					( element ) => {
						cssClass = (element === ' ' ? 'qodef-m-empty-char' : ' ');
						$textHolder.append( '<span class="qodef-m-char ' + cssClass + '">' + element + '</span>' );
					}
				);

				setTimeout(
					() => {
						qodefTextualSpinner.animateSpinner( $holder );
					}, 100
				);
			}
		},
		animateSpinner ( $holder ) {
			$holder.addClass( 'qodef--init' );

			function animationLoop ( animationProps ) {
				var $chars      = $holder.find( '.qodef-m-char' ),
					charsLength = $chars.length - 1;

				if ( $chars.length ) {
					$chars.each(
						( index, element ) => {
							var $thisChar = $( element );

							setTimeout(
								() => {
									$thisChar.animate(
									    animationProps.type,
										animationProps.duration,
										animationProps.easing,
										() => {
											if ( index === charsLength ) {
												if ( 1 === animationProps.repeat ) {
													animationLoop(
													    {
                                                            type: { opacity: 0 },
                                                            duration: 1200,
                                                            easing: 'swing',
                                                            delay: 0,
                                                            repeat: 0,
                                                        }
													);
												} else {
													if ( ! qodefTextualSpinner.windowLoaded ) {
														animationLoop(
														    {
                                                                type: { opacity: 1 },
                                                                duration: 1800,
                                                                easing: 'swing',
                                                                delay: 160,
                                                                repeat: 1,
                                                            }
														);
													} else {
														qodefTextualSpinner.fadeOutLoader(
															$holder,
															600,
															0,
															'swing'
														);

														setTimeout(
															() => {
																var $revSlider = $( '.qodef-after-spinner-rev rs-module' );

																if ( $revSlider.length ) {
																	$revSlider.revstart();
																}
															}, 800
														);
													}
												}
											}
										}
									);
								}, index * animationProps.delay
							);
						}
					);
				}
			}

			animationLoop (
			    {
                    type: { opacity: 1 },
                    duration: 1800,
                    easing: 'swing',
                    delay: 160,
                    repeat: 1,
                }
			);
		},
		fadeOutLoader( $holder, speed, delay, easing ) {
			speed  = speed ? speed : 500;
			delay  = delay ? delay : 0;
			easing = easing ? easing : 'swing';

			if ( $holder.length ) {
				$holder.delay( delay ).fadeOut( speed, easing );

				$( window ).on(
					'bind',
					'pageshow',
					function( event ) {

						if ( event.originalEvent.persisted ) {
							$holder.fadeOut( speed, easing );
						}
					}
				);
			}
		}
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_instagram_list = {};

	$( document ).ready(
		function () {
			qodefInstagram.init();
		}
	);

	var qodefInstagram = {
		init: function () {
			this.holder = $( '.qodef-instagram-list #sb_instagram' );

			if ( this.holder.length ) {
				this.holder.each(
					function () {

						if ( $( this ).parent().hasClass( 'qodef-instagram-columns' ) ) {
							var $imagesHolder  = $( this ).find( '#sbi_images' ),
								$images        = $imagesHolder.find( '.sbi_item.sbi_type_image, .sbi_item.sbi_type_carousel' ),
								initialPadding = $imagesHolder.css( 'padding' );

							// remove some unnecessary paddings
							$imagesHolder.css('padding', '0');
							$imagesHolder.css('margin', '-' + initialPadding);
							$imagesHolder.css('width', 'calc(100% + ' + ( initialPadding) + ' + ' + ( initialPadding) + ')');

							$images.attr('style', 'padding: ' + initialPadding + '!important');
						} else if ( $( this ).parent().hasClass( 'qodef-instagram-slider' ) ) {
							qodefInstagram.initSlider( $( this ) );
						}
					}
				);
			}
		},
		initSlider: function ( $currentItem, $initAllItems ) {

			var $imagesHolder  = $currentItem.find( '#sbi_images' ),
				$images        = $currentItem.find( '.sbi_item.sbi_type_image' ),
				initialPadding = $imagesHolder.css( 'padding' );

			// remove some unnecessary paddings
			$imagesHolder.css('padding', '0');
			$images.css('padding', '0');

			// items will inherit this margin
			$imagesHolder.attr('style', 'margin-right: ' + (parseInt( initialPadding ) * 2) + 'px !important');

			var sliderOptions = {};

			sliderOptions.spaceBetween      = parseInt( initialPadding ) * 2;
			sliderOptions.customStages      = true;
			sliderOptions.slidesPerView     = $currentItem.data( 'cols' ) !== undefined && $currentItem.data( 'cols' ) !== '' ? $currentItem.data( 'cols' ) : 3;
			sliderOptions.slidesPerView1024 = $currentItem.data( 'cols' ) !== undefined && $currentItem.data( 'cols' ) !== '' ? $currentItem.data( 'cols' ) : 3;
			sliderOptions.slidesPerView680  = $currentItem.data( 'colstablet' ) !== undefined && $currentItem.data( 'colstablet' ) !== '' ? $currentItem.data( 'colstablet' ) : 2;
			sliderOptions.slidesPerView480  = $currentItem.data( 'colsmobile' ) !== undefined && $currentItem.data( 'colsmobile' ) !== '' ? $currentItem.data( 'colsmobile' ) : 1;

			$currentItem.attr( 'data-options', JSON.stringify(sliderOptions) );

			$imagesHolder.addClass( 'swiper-wrapper' );

			if ( $images.length ) {
				$images.each(
					function () {
						$( this ).addClass( 'qodef-e qodef-image-wrapper swiper-slide' );
					}
				);
			}

			if ( typeof qodef.qodefSwiper === 'object' ) {

				if ( false === $initAllItems ) {
					qodef.qodefSwiper.initSlider( $currentItem );
				} else {
					qodef.qodefSwiper.init( $currentItem );
				}
			}
		},
	};

	qodefCore.shortcodes.luxedrive_core_instagram_list.qodefInstagram = qodefInstagram;
	qodefCore.shortcodes.luxedrive_core_instagram_list.qodefSwiper    = qodef.qodefSwiper;

})( jQuery );

(function ( $ ) {
	'use strict';

	/*
	 **	Re-init scripts on gallery loaded
	 */
	$( document ).on(
		'yith_wccl_product_gallery_loaded',
		function () {

			if ( typeof qodefCore.qodefWooMagnificPopup === 'function' ) {
				qodefCore.qodefWooMagnificPopup.init();
			}
		}
	);

})( jQuery );

(function ($) {
	'use strict';

	$(document).on(
		'qv_loader_stop qv_variation_gallery_loaded',
		function () {
			qodefYithSelect2.init();
		}
	);

	var qodefYithSelect2 = {
		init: function (settings) {
			this.holder = [];
			this.holder.push(
				{
					holder: $('#yith-quick-view-modal .variations select'),
					options: {
						minimumResultsForSearch: Infinity
					}
				}
			);

			// Allow overriding the default config
			$.extend(this.holder, settings);

			if (typeof this.holder === 'object') {
				$.each(
					this.holder,
					function (key, value) {
						qodefYithSelect2.createSelect2(value.holder, value.options);
					}
				);
			}
		},
		createSelect2: function ($holder, options) {
			if (typeof $holder.select2 === 'function') {
				$holder.select2(options);
			}
		}
	};

})(jQuery);

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_product_category_list                    = {};
	qodefCore.shortcodes.luxedrive_core_product_category_list.qodefMasonryLayout = qodef.qodefMasonryLayout;
	qodefCore.shortcodes.luxedrive_core_product_category_list.qodefSwiper        = qodef.qodefSwiper;

})( jQuery );

(function ( $ ) {
	'use strict';

	var shortcode = 'luxedrive_core_product_list';

	qodefCore.shortcodes[shortcode] = {};

	if ( typeof qodefCore.listShortcodesScripts === 'object' ) {
		$.each(
			qodefCore.listShortcodesScripts,
			function ( key, value ) {
				qodefCore.shortcodes[shortcode][key] = value;
			}
		);
	}

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function () {
			qodefDropDownCart.init();
		}
	);

	var qodefDropDownCart = {
		init: function () {
			var $holder = $( '.qodef-widget-dropdown-cart-content' );

			if ( $holder.length ) {
				$holder.off().each(
					function () {
						var $thisHolder = $( this );

						qodefDropDownCart.trigger( $thisHolder );

						qodefCore.body.on(
							'added_to_cart removed_from_cart',
							function () {
								qodefDropDownCart.init();
							}
						);
					}
				);
			}
		},
		trigger: function ( $holder ) {
			var $items = $holder.find( '.qodef-woo-mini-cart' );
			if ( $items.length && typeof qodefCore.qodefPerfectScrollbar === 'object' ) {
				qodefCore.qodefPerfectScrollbar.init( $items );
			}
		},
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	$( document ).ready(
		function () {
			qodefSideAreaCart.init();
		}
	);

	var qodefSideAreaCart = {
		init: function () {
			var $holder = $( '.widget_luxedrive_core_woo_side_area_cart' );

			if ( $holder.length ) {
				$holder.off().each(
					function () {
						var $thisHolder = $( this );

						if ( qodefCore.windowWidth > 680 ) {
							qodefSideAreaCart.trigger( $thisHolder );
							qodefSideAreaCart.start( $thisHolder );

							qodefCore.body.on(
								'added_to_cart removed_from_cart wc_fragments_refreshed',
								function () {
									qodefSideAreaCart.init();
								}
							);

						}
					}
				);
			}
		},
		trigger: function ( $holder ) {
			var $items = $holder.find( '.qodef-woo-side-area-cart' );
			if ( $items.length && typeof qodefCore.qodefPerfectScrollbar === 'object' ) {
				qodefCore.qodefPerfectScrollbar.init( $items );
			}
		},
		start: function ( $holder ) {
			$holder.on(
				'click',
				'.qodef-m-opener',
				function ( e ) {
					e.preventDefault();

					if ( ! $holder.hasClass( 'qodef--opened' ) ) {
						qodefSideAreaCart.openSideArea( $holder );
						qodefSideAreaCart.trigger( $holder );

						$( document ).keyup(
							function ( e ) {
								if ( e.keyCode === 27 ) {
									qodefSideAreaCart.closeSideArea( $holder );
								}
							}
						);
					} else {
						qodefSideAreaCart.closeSideArea( $holder );
					}
				}
			);

			$holder.on(
				'click',
				'.qodef-m-close',
				function ( e ) {
					e.preventDefault();
					qodefSideAreaCart.closeSideArea( $holder );
				}
			);
		},
		openSideArea: function ( $holder ) {
			qodefCore.qodefScroll.disable();

			$holder.addClass( 'qodef--opened' );

			$( '#qodef-page-wrapper' ).prepend( '<div class="qodef-woo-side-area-cart-cover"><div class="qodef-woo-side-area-overlay"></div></div>' );
			var $closeSvg = $holder.find( '.qodef-widget-side-area-cart-content .qodef-m-close' ),
				$overlay  = $( '.qodef-woo-side-area-cart-cover' );

			$overlay.prepend( $closeSvg );

			qodefSideAreaCart.initCloseCursor(
				$overlay,
				$closeSvg,
				$holder
			);

			$( '.qodef-woo-side-area-cart-cover' ).on(
				'click',
				function ( e ) {
					e.preventDefault();

					qodefSideAreaCart.closeSideArea( $holder );
				}
			);
		},
		closeSideArea: function ( $holder ) {
			if ( $holder.hasClass( 'qodef--opened' ) ) {
				qodefCore.qodefScroll.enable();

				var $closeSvg = $( '.qodef-woo-side-area-cart-cover .qodef-m-close' );
				$holder.find( '.qodef-widget-side-area-cart-content' ).prepend( $closeSvg );

				$holder.removeClass( 'qodef--opened' );
				$( '.qodef-woo-side-area-cart-cover' ).remove();
			}
		},
		initCloseCursor: function ( $overlay, $cursor, $content ) {
			$overlay.on(
				'mouseenter',
				function () {
					$cursor.addClass( 'qodef--active' );
				}
			).on(
				'mouseleave',
				function () {
					$cursor.removeClass( 'qodef--active' );
				}
			);

			$( window ).on(
				'mousemove',
				function ( e ) {
					if ( $cursor.hasClass( 'qodef--active' ) ) {
						var x      = e.clientX,
							y      = e.clientY,
							deltaY = $cursor.height() / 2,
							deltaX = $cursor.width() / 2;

						$cursor.css( {
							'top': y - deltaY,
							'left': x - deltaX
						} );
					}
				}
			);

			$content.on(
				'mouseenter',
				function () {
					$cursor.removeClass( 'qodef--active' );
				}
			).on(
				'mouseleave',
				function () {
					$cursor.addClass( 'qodef--active' );
				}
			);
		},
	};

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_clients_list             = {};
	qodefCore.shortcodes.luxedrive_core_clients_list.qodefSwiper = qodef.qodefSwiper;

})( jQuery );

(function ( $ ) {
	'use strict';

	var shortcode = 'luxedrive_core_masonry_gallery_list';

	qodefCore.shortcodes[shortcode]                    = {};
	qodefCore.shortcodes[shortcode].qodefMasonryLayout = qodef.qodefMasonryLayout;

})( jQuery );

(function ( $ ) {
	'use strict';

	var shortcode = 'luxedrive_core_team_list';

	qodefCore.shortcodes[shortcode] = {};

	if ( typeof qodefCore.listShortcodesScripts === 'object' ) {
		$.each(
			qodefCore.listShortcodesScripts,
			function ( key, value ) {
				qodefCore.shortcodes[shortcode][key] = value;
			}
		);
	}

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_testimonials_list = {};
	
	$( window ).on( 'load',
		function () {
			qodefTestimonialsList.init();
		}
	);
	
	var qodefTestimonialsList = {
		init: function () {
			this.holder = $( '.qodef-testimonials-list.qodef-swiper-container' );
			
			if ( this.holder.length ) {
				this.holder.each(
					function () {
						qodefTestimonialsList.equalizeHeight( $( this ) );
					}
				);
			}
		},
		equalizeHeight: function ( $currentList ) {
			var items         = $currentList.find('.qodef-e-inner'),
				maxHeight     = 0;
			
			if ( qodef.windowWidth > 680 ) {
				maxHeight = $.makeArray( items ).map( e => e.offsetHeight).reduce( ( prev, curr ) => {
					return prev >= curr ? prev : curr;
				}, 0 );
				
				if ( items.length ) {
					items.each(
						function () {
							$( this ).height( maxHeight );
						}
					);
				}
			}
		},
	};
	
	qodefCore.shortcodes.luxedrive_core_testimonials_list.qodefSwiper = qodef.qodefSwiper;
	qodefCore.shortcodes.luxedrive_core_testimonials_list.qodefTestimonialsList = qodefTestimonialsList;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_vehicle_booking_form = {};

	$( document ).ready( function () {
		qodefBookingForm.init();
	} );

	var qodefBookingForm = {
		init: function () {
			this.holder = $( '.qodef-vehicle-booking-form' );

			if ( this.holder.length ) {
				this.holder.each( function () {
					var $thisHolder = $( this );

					qodefBookingForm.initDatePicker( $thisHolder );
					qodefBookingForm.initTimePicker( $thisHolder );
					qodefBookingForm.initSelect2( $thisHolder );

					var form         = $thisHolder.find( 'form' ),
						typeVehicle  = $thisHolder.data( 'type-vehicle' ),
						formVehicles = $thisHolder.find( 'select.qodef-booking-vehicles' ),
						formTypes    = $thisHolder.find( 'select.qodef-booking-types' ),
						responseDiv  = $thisHolder.find( '.qodef-m-response' );

					formTypes.on(
						'change',
						function ( e ) {
							formVehicles.find( 'option' ).not( ':first-child' ).remove();

							var newHtml    = '';
							var newDoctors = typeVehicle[e.target.value];
							for ( var i = 0; typeof newDoctors !== 'undefined' && i < newDoctors.length; i++ ) {
								newHtml += '<option value="' + newDoctors[i].id + '">' + newDoctors[i].name + '</option>';
							}

							formVehicles.append( newHtml );
						}
					);

					form.on(
						'submit',
						function ( e ) {
							e.preventDefault();

							var enquiryData = {
								vehicle_type: form.find( '*[name="qodef-booking-type"]' ).val(),
								vehicle: form.find( '*[name="qodef-booking-vehicle"]' ).val(),
								period: form.find( '*[name="qodef-booking-period"]' ).val(),
								date: form.find( 'input.qodef-m-date' ).val(),
								time: form.find( 'input.qodef-m-time' ).val(),
								name: form.find( 'input.qodef-booking-name' ).val(),
								passengers: form.find( 'input.qodef-booking-passengers' ).val(),
								email: form.find( 'input.qodef-booking-email' ).val(),
								contact: form.find( 'input.qodef-booking-contact' ).val(),
								message: form.find( 'textarea.qodef-booking-request' ).val(),
							};

							$.ajax( {
								type: 'POST',
								data: {
									options: enquiryData,
								},
								url: qodefGlobal.vars.restUrl + qodefGlobal.vars.bookingFormRestRoute,
								beforeSend: function ( request ) {
									request.setRequestHeader(
										'X-WP-Nonce',
										qodefGlobal.vars.restNonce
									);
								},
								success: function ( response ) {
									responseDiv.html( response.data ).slideDown( 300 );
									setTimeout(
										function () {
											responseDiv.slideUp(
												300,
												function () {
													responseDiv.html( '' );
												}
											);
										},
										3000
									);
								}
							} );
						}
					);
				} );
			}
		},
		initSelect2: function ( $holder ) {
			var $selects = $holder.find( '.qodef-select2' );

			if ( $selects.length ) {
				$selects.each( function () {
					if ( typeof $( this ).select2 === 'function' ) {
						$( this ).select2( {
							minimumResultsForSearch: -1,
						} );
					}
				} );
			}
		},
		initDatePicker: function ( $holder ) {
			var $datepickers = $holder.find( '.qodef-m-date' );

			if ( $datepickers.length ) {
				$datepickers.each( function () {
					$( this ).datepicker( {
						prevText: '<span class="arrow_carrot-left"></span>',
						nextText: '<span class="arrow_carrot-right"></span>',
						dateFormat: 'd/m/y'
					} );
				} );
			}
		},
		initTimePicker: function ( $holder ) {
			var $timepickers = $holder.find( '.qodef-m-time' );

			if ( $timepickers.length ) {
				$timepickers.each( function () {
					$( this ).timepicker( {
						timeFormat: 'hh:mm p',
						interval: 30,
						minTime: '09:00 am',
						maxTime: '06:00 pm',
						dynamic: false,
						dropdown: true,
						scrollbar: true
					} );
				} );
			}
		}
	};

	qodefCore.shortcodes.luxedrive_core_vehicle_booking_form.qodefBookingForm = qodefBookingForm;

})( jQuery );

(function ( $ ) {
	'use strict';

	var shortcode = 'luxedrive_core_vehicle_list';

	qodefCore.shortcodes[shortcode] = {};

	if ( typeof qodefCore.listShortcodesScripts === 'object' ) {
		$.each(
			qodefCore.listShortcodesScripts,
			function ( key, value ) {
				qodefCore.shortcodes[shortcode][key] = value;
			}
		);
	}

	$( window ).on('load',
		function () {
			qodefVehicleFilter.initSelect2();
		}
	);

	$( document ).ready(
		function() {
			qodefVehicleFilter.init();
		}
	);

	var qodefVehicleFilter = {
		list: {},
		fields: {},
		init: function () {
			var $vehicleList = $('.qodef-vehicle-list.qodef-filter--enabled');

			if ($vehicleList.length) {
				$vehicleList.each( function( ) {
					var $thisList = $( this );

					qodefVehicleFilter.list = $thisList;
					qodefVehicleFilter.activeState( $thisList );
					qodefVehicleFilter.initSearchParams( $thisList );
				});
			}
		},
		initSearchParams: function ( $vehicleList ) {
			var $fields  = [],
				$select = $vehicleList.find('.qodef-filter-tax');

			$fields.$selectFields = $vehicleList.find('.qodef-filter-tax option');
			$fields.selectFieldsExists = $fields.$selectFields.length;

			qodefVehicleFilter.fields = $fields;

			$select.on('change', {productList: $vehicleList, fields: $fields}, function ( e ) {
				qodefVehicleFilter.initFilter( $vehicleList, $fields );

				$select.blur();
			});
		},
		activeState: function( $vehicleList ) {
			var $selectFields = $vehicleList.find('.qodef-filter-tax');

			if( $selectFields.length ) {
				$selectFields.each(function() {
					var $select = $(this);

					$select.on('change', function() {
						var $field = $(this).find('option[value="' + $(this).val() + '"]');

						$field.attr('selected', true);
						$field.siblings().attr('selected',false);
					});
				});
			}
		},
		initFilter: function ( $list, $items ) {
			var $vehicleList = $list,
				options      = $vehicleList.data( 'options' ),
				$fields      = $items,
				newOptions   = {};

			if ( 'vehicle-tag' === options['tax'] ) {
				newOptions['vehicle-tag'] = [];
				newOptions['vehicle-tag'].push(options['tax_slug']);
				newOptions['vehicle-tag'] = newOptions['vehicle-tag'].join( ',' );
			}

			if ($fields.selectFieldsExists) {
				var $selected = $vehicleList.find('.qodef-filter-tax option[selected="selected"]');

				newOptions['vehicle-type'] = [];
				newOptions['vehicle-make'] = [];
				newOptions['vehicle-color'] = [];

				if ( 'vehicle-type' === options['tax'] ) {
					newOptions['vehicle-type'].push(options['tax_slug']);
				}

				if ( 'vehicle-make' === options['tax'] ) {
					newOptions['vehicle-make'].push(options['tax_slug']);
				}

				if ( 'vehicle-color' === options['tax'] ) {
					newOptions['vehicle-color'].push(options['tax_slug']);
				}

				$selected.each(
					function () {
						var item = $(this);
						switch ( item.parent().attr('name') ) {
							case 'filter-vehicle-type':
								var fieldKey = 'vehicle-type',
									value = item.attr('value');
								if (typeof value !== "undefined" && value !== "") {
									newOptions[fieldKey].push(item.attr('value'));
								} else {
									newOptions[fieldKey] = '';
								}
								break;
							case 'filter-vehicle-make':
								var fieldKey = 'vehicle-make',
									value = item.attr('value');
								if (typeof value !== "undefined" && value !== "") {
									newOptions[fieldKey].push(item.attr('value'));
								} else {
									newOptions[fieldKey] = '';
								}
								break;
							case 'filter-vehicle-color':
								var fieldKey = 'vehicle-color',
									value = item.attr('value');
								if (typeof value !== "undefined" && value !== "") {
									newOptions[fieldKey].push(item.attr('value'));
								} else {
									newOptions[fieldKey] = '';
								}
								break;
						}
					}
				);

				newOptions['vehicle-type'] = newOptions['vehicle-type'].join( ',' );
				newOptions['vehicle-make'] = newOptions['vehicle-make'].join( ',' );
				newOptions['vehicle-color'] = newOptions['vehicle-color'].join( ',' );
			}

			var additional = qodefVehicleFilter.createAdditionalQuery( newOptions );

			$.each(
				additional,
				function (key, value) {
					options[key] = value;
				}
			);

			$vehicleList.data( 'options', options );
			qodef.body.trigger( 'luxedrive_trigger_load_more', [$vehicleList, 1] );
		},
		createAdditionalQuery: function( newOptions ){
			var addQuery 		= {},
				i = 0;

			addQuery.additional_query_args 			  = {};
			addQuery.additional_query_args.tax_query  = {};
			addQuery.additional_query_args.meta_query = {};

			if (typeof newOptions === 'object') {
				$.each(
					newOptions,
					function ( key, value ) {
						switch (key) {
							case 'vehicle-type':
								if ( value !== '' && value !== '*' ) {
									if ( value.indexOf( ',' ) !== -1 ) {
										value = value.split( ',' );
									}
									addQuery.additional_query_args.tax_query['value' + i]          = {};
									addQuery.additional_query_args.tax_query['value' + i].taxonomy = 'vehicle-type';
									addQuery.additional_query_args.tax_query['value' + i].field    = typeof value === 'number' ? 'term_id' : 'slug';
									addQuery.additional_query_args.tax_query['value' + i].terms    = value;
									addQuery.additional_query_args.tax_query['value' + i].operator = 'IN';
									i++;
								}
								break;
							case 'vehicle-make':
								if ( value !== '' && value !== '*' ) {
									if ( value.indexOf( ',' ) !== -1 ) {
										value = value.split( ',' );
									}
									addQuery.additional_query_args.tax_query['value' + i]          = {};
									addQuery.additional_query_args.tax_query['value' + i].taxonomy = 'vehicle-make';
									addQuery.additional_query_args.tax_query['value' + i].field    = typeof value === 'number' ? 'term_id' : 'slug';
									addQuery.additional_query_args.tax_query['value' + i].terms    = value;
									addQuery.additional_query_args.tax_query['value' + i].operator = 'IN';
									i++;
								}
								break;
							case 'vehicle-color':
								if ( value !== '' && value !== '*' ) {
									if ( value.indexOf( ',' ) !== -1 ) {
										value = value.split( ',' );
									}
									addQuery.additional_query_args.tax_query['value' + i]          = {};
									addQuery.additional_query_args.tax_query['value' + i].taxonomy = 'vehicle-color';
									addQuery.additional_query_args.tax_query['value' + i].field    = typeof value === 'number' ? 'term_id' : 'slug';
									addQuery.additional_query_args.tax_query['value' + i].terms    = value;
									addQuery.additional_query_args.tax_query['value' + i].operator = 'IN';
									i++;
								}
								break;
							case 'vehicle-tag':
								if ( value !== '' && value !== '*' ) {
									if ( value.indexOf( ',' ) !== -1 ) {
										value = value.split( ',' );
									}
									addQuery.additional_query_args.tax_query['value' + i]          = {};
									addQuery.additional_query_args.tax_query['value' + i].taxonomy = 'vehicle-tag';
									addQuery.additional_query_args.tax_query['value' + i].field    = typeof value === 'number' ? 'term_id' : 'slug';
									addQuery.additional_query_args.tax_query['value' + i].terms    = value;
									addQuery.additional_query_args.tax_query['value' + i].operator = 'IN';
									i++;
								}
								break;
						}
					}
				);

				if ( Object.entries( addQuery.additional_query_args.tax_query ).length > 1 ) {
					addQuery.additional_query_args.tax_query['relation'] = 'AND';
				}
			}

			if ( $.isEmptyObject( addQuery.additional_query_args.tax_query ) ) {
				delete addQuery.additional_query_args.tax_query;
			}

			return addQuery;
		},
		initSelect2: function() {
			var $vehicleList = $('.qodef-vehicle-list.qodef-filter--enabled');

			if ($vehicleList.length) {
				$vehicleList.each( function( ){
					var $select = $vehicleList.find( '.qodef-filter-tax' );

					if ( $select.length && typeof $select.select2 === 'function' ) {
						$select.select2(
							{
								minimumResultsForSearch: Infinity,
							}
						);
					}
				} );
			}
		},
	};

	qodefCore.shortcodes.luxedrive_core_vehicle_list.qodefVehicleFilter = qodefVehicleFilter;

})( jQuery );

(function ( $ ) {
	'use strict';

	qodefCore.shortcodes.luxedrive_core_vehicle_tabbed_list = {};

	$( document ).ready(
		function () {
			qodefTabbedList.init();
		}
	);

	var qodefTabbedList = {
		init: function () {
			var $holder = $( '.qodef-vehicle-tabbed-list .qodef-e-items-wrapper' );

			if ( $holder.length ) {
				$holder.each(
					function () {
						qodefTabbedList.initAccordion( $( this ) );
					}
				);
			}
		},
		initAccordion: function ( $accordion ) {
			var $acc = $accordion.accordion(
				{
					animate: 'swing',
					collapsible: true,
					active: 0,
					icons: '',
					heightStyle: 'content',
				}
			);
			
			var $links = $accordion.find('a');
			
			$links.on('click', function ( e ) {
				$accordion.accordion( 'disable' );
				e.target.click();
			});
		},
	};

	qodefCore.shortcodes.luxedrive_core_vehicle_tabbed_list.qodefTabbedList = qodefTabbedList;

})( jQuery );
