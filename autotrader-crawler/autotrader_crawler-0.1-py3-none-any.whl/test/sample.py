SAMPLE_PAGE = '''<div class="js-search-results">
    <div class="js-banner-loader-turn-off" data-feature=""></div>


        <header class="search-page__header js-search-page__header">

                <ul class="searchResults__buttonBar searchResults__buttonBar-all atc-tabline-group">
                    <li class='searchResults__buttonBar-tab atc-tabline'><button class="js-tab-all tab-all tracking-standard-link atc-tabline__link" data-label="bb search all" title='Search all cars'>All</button></li>
                    <li class='searchResults__buttonBar-tab atc-tabline'><button class="js-tab-new tab-new tracking-standard-link atc-tabline__link" data-label="bb search new" title='Search new cars'>New</button></li>
                    <li class='searchResults__buttonBar-tab atc-tabline'><button class="js-tab-used tab-used tracking-standard-link atc-tabline__link" data-label="bb search used" title='Search used cars'>Used</button></li>
                </ul>

            <div class="search-page__sort-options">
                <label class="sort-option">

                    <span class="sort-option__label">

                        Sort by:

                    </span>

                    <div class="sort-option__field js-sort-option__field">

                        <div class="selectbox">

                            <select class="js-sort-options js-selectbox selectbox__select">
                                                <option selected="selected" value="sponsored">Sponsored adverts first</option>
                                                                <option  value="price-asc">Price (Lowest)</option>
                                                                <option  value="price-desc">Price (Highest)</option>
                                                                <option  value="distance">Distance</option>
                                                                <option  value="make">Make</option>
                                                                <option  value="model">Model</option>
                                                                <option  value="mileage">Mileage</option>
                                                                <option  value="year-desc">Age (Newest first)</option>
                                                                <option  value="relevance">Relevance</option>
                                                
                            </select>

                            <div class="selectbox__label white-selectbox js-selectbox__label">
                                                    Sponsored adverts first
                                                                                                                                                                                </div>
                        </div>
                    </div>
                </label>

                    <div class="sort-option__info-tooltip js-sort-option__info-tooltip is-hidden">
                        <i class="icon icon-info">
                            <svg class="sort-option__info-icon">
                                <title>Info Icon</title>
                                <use xlink:href="/templates/_generated/svg_icons/common.svg#icon-info"></use>
                            </svg>
                        </i>
                        <div class="speech-bubble">
                            <p class="speech-bubble__text">
                                Our default sort order is Relevance, which takes into account advert quality and popularity. Sponsored adverts will appear first.
                            </p>
                        </div>
                    </div>
            </div>
        </header>

        <var id="fpa-navigation" fpa-navigation="{&quot;totalMatchingResults&quot;:411,&quot;fpaNavigation&quot;:[{&quot;shortAdvertForFPANavigation&quot;:[{&quot;id&quot;:&quot;201906259399630&quot;,&quot;fpaUrl&quot;:&quot;/classified/advert/201906259399630?make\u003dPORSCHE\u0026advertising-location\u003dat_cars\u0026model\u003dPANAMERA\u0026radius\u003d1500\u0026sort\u003dsponsored\u0026postcode\u003dn1c4ag\u0026onesearchad\u003dUsed\u0026onesearchad\u003dNearly%20New\u0026onesearchad\u003dNew\u0026page\u003d2&quot;},{&quot;id&quot;:&quot;201909212476563&quot;,&quot;fpaUrl&quot;:&quot;/classified/advert/201909212476563?make\u003dPORSCHE\u0026advertising-location\u003dat_cars\u0026model\u003dPANAMERA\u0026radius\u003d1500\u0026sort\u003dsponsored\u0026postcode\u003dn1c4ag\u0026onesearchad\u003dUsed\u0026onesearchad\u003dNearly%20New\u0026onesearchad\u003dNew\u0026page\u003d2&quot;},{&quot;id&quot;:&quot;201908271568643&quot;,&quot;fpaUrl&quot;:&quot;/classified/advert/201908271568643?make\u003dPORSCHE\u0026advertising-location\u003dat_cars\u0026model\u003dPANAMERA\u0026radius\u003d1500\u0026sort\u003dsponsored\u0026postcode\u003dn1c4ag\u0026onesearchad\u003dUsed\u0026onesearchad\u003dNearly%20New\u0026onesearchad\u003dNew\u0026page\u003d2&quot;},{&quot;id&quot;:&quot;201906289507830&quot;,&quot;fpaUrl&quot;:&quot;/classified/advert/201906289507830?make\u003dPORSCHE\u0026advertising-location\u003dat_cars\u0026model\u003dPANAMERA\u0026radius\u003d1500\u0026sort\u003dsponsored\u0026postcode\u003dn1c4ag\u0026onesearchad\u003dUsed\u0026onesearchad\u003dNearly%20New\u0026onesearchad\u003dNew\u0026page\u003d2&quot;},{&quot;id&quot;:&quot;201908050811645&quot;,&quot;fpaUrl&quot;:&quot;/classified/advert/201908050811645?make\u003dPORSCHE\u0026advertising-location\u003dat_cars\u0026model\u003dPANAMERA\u0026radius\u003d1500\u0026sort\u003dsponsored\u0026postcode\u003dn1c4ag\u0026onesearchad\u003dUsed\u0026onesearchad\u003dNearly%20New\u0026onesearchad\u003dNew\u0026page\u003d2&quot;},{&quot;id&quot;:&quot;201904056639410&quot;,&quot;fpaUrl&quot;:&quot;/classified/advert/201904056639410?make\u003dPORSCHE\u0026advertising-location\u003dat_cars\u0026model\u003dPANAMERA\u0026radius\u003d1500\u0026sort\u003dsponsored\u0026postcode\u003dn1c4ag\u0026onesearchad\u003dUsed\u0026onesearchad\u003dNearly%20New\u0026onesearchad\u003dNew\u0026page\u003d2&quot;},{&quot;id&quot;:&quot;201907250430713&quot;,&quot;fpaUrl&quot;:&quot;/classified/advert/201907250430713?make\u003dPORSCHE\u0026advertising-location\u003dat_cars\u0026model\u003dPANAMERA\u0026radius\u003d1500\u0026sort\u003dsponsored\u0026postcode\u003dn1c4ag\u0026onesearchad\u003dUsed\u0026onesearchad\u003dNearly%20New\u0026onesearchad\u003dNew\u0026page\u003d2&quot;},{&quot;id&quot;:&quot;201908090958000&quot;,&quot;fpaUrl&quot;:&quot;/classified/advert/201908090958000?make\u003dPORSCHE\u0026advertising-location\u003dat_cars\u0026model\u003dPANAMERA\u0026radius\u003d1500\u0026sort\u003dsponsored\u0026postcode\u003dn1c4ag\u0026onesearchad\u003dUsed\u0026onesearchad\u003dNearly%20New\u0026onesearchad\u003dNew\u0026page\u003d2&quot;},{&quot;id&quot;:&quot;201906219242547&quot;,&quot;fpaUrl&quot;:&quot;/classified/advert/201906219242547?make\u003dPORSCHE\u0026advertising-location\u003dat_cars\u0026model\u003dPANAMERA\u0026radius\u003d1500\u0026sort\u003dsponsored\u0026postcode\u003dn1c4ag\u0026onesearchad\u003dUsed\u0026onesearchad\u003dNearly%20New\u0026onesearchad\u003dNew\u0026page\u003d2&quot;},{&quot;id&quot;:&quot;201905117852537&quot;,&quot;fpaUrl&quot;:&quot;/classified/advert/201905117852537?make\u003dPORSCHE\u0026advertising-location\u003dat_cars\u0026model\u003dPANAMERA\u0026radius\u003d1500\u0026sort\u003dsponsored\u0026postcode\u003dn1c4ag\u0026onesearchad\u003dUsed\u0026onesearchad\u003dNearly%20New\u0026onesearchad\u003dNew\u0026page\u003d2&quot;}],&quot;pageInSearch&quot;:2}],&quot;totalPages&quot;:42,&quot;currentPage&quot;:2}"></var>


        <ul class="search-page__results">




                                        <li class="search-page__result"
                                            id="201909252598088"

                                            data-search-results-advert-card
                                            data-advert-id="201909252598088"

                                            data-is-featured-listing="true"

                                            data-image-count="30"
                                            data-is-manufacturer-approved="true"
                                            data-has-finance="true"
                                            data-is-franchise-approved="false"
                                            data-good-great-value="high"
                                            data-distance-value="363 miles"
                                            data-condition-value=""
                                        >
                                                <span class="listings-standout">Featured listing</span><article
                                                        data-standout-type="featured-listing"
                                                        class="js-standout-listing  search-listing
                                                 sso-listing 

                                                ">
                                                    <section class="content-column">
                                                            <figure class="listing-main-image">
                                                                <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa rel="nofollow" href="/classified/advert/201909252598088?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">

                                                                <div class="listing-image-count" data-label="search appearance click ">
                                                                    <i data-label="search appearance click " class="listing-image-icon">
                                                                        <svg>
                                                                            <use xlink:href="/templates/_generated/svg_icons/search-listings.svg#icon-camera"></use>
                                                                        </svg>
                                                                    </i> 30


                                                                    <!--replace with hasSpin-->
                                                                </div>

                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w260h196pd8d8d8/b9ba0685b6bc4003935d79664e703837.jpg"/>
                                                                </a>
                                                            </figure>
                                                        <div class="information-container">
                                                            <h2 class="listing-title title-wrap">
                                                                <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " rel="nofollow" href="/classified/advert/201909252598088?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">Porsche Panamera Diesel Saloon 3.0 [300] V6 Diesel 4dr Tiptronic S</a>
                                                            </h2>
                                                            <p class="listing-attention-grabber ">AirSuspension/Sunroof/BOSE</p>
                                                            <ul class="listing-key-specs ">


                                                                            <li>2015 (15 reg)</li>
                                                                            
                                                                            <li>Hatchback</li>
                                                                            
                                                                            <li>37,847 miles</li>
                                                                            
                                                                            <li>3.0L</li>
                                                                            
                                                                            <li>300bhp</li>
                                                                            
                                                                            <li>Automatic</li>
                                                                            
                                                                            <li>Diesel</li>
                                                                            

                                                                </ul>
                                                             <ul class="listing-extra-detail">
                                                                        <li>Manufacturer Approved</li>



                                                             </ul>


                                                                    <p class="listing-description">An incredible opportunity to combine comfort, elegance and economy behind the &hellip;</p>
                                                            <div class="seller-info seller-profile-link">
                                                                <div class="seller-type  trade-seller">
                                                                                Trade seller - <a href="/dealers/porsche-centre-perth-10013602" rel="nofollow">See all 31 cars</a>
                                                                </div>


                                                                            <div class="seller-location">
                                                                                    363 miles away
                                                                            </div>
                                                            </div>
                                                        </div>
                                                            <a class=" js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa href="/classified/advert/201909252598088?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" rel="nofollow">
                                                                <ul class="listing__thumbnails">
                                                                            <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/b8fdb371c10143aeb887bab4ad2396db.jpg" alt=""/>
                                                                            </li>
                                                                                    <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/e1d9d285487d4f389cac614e28e03997.jpg" alt=""/>
                                                                            </li>
                                                                                    <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/6a70dc4c117d4a4193e3a418d04c3f53.jpg" alt=""/>
                                                                            </li>
                                                                                    <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/a524c8db16fc4518aa6f57d609f1fc00.jpg" alt=""/>
                                                                            </li>
                                                                                    <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/5dac75fbc17d4d65b4bbb937173f8032.jpg" alt=""/>
                                                                            </li>
                                                                                    <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/5532a596ce3b47879a5cade15258e3db.jpg" alt=""/>
                                                                            </li>
                                                                                    <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/7a357e510fd54b92ace432a86f775b58.jpg" alt=""/>
                                                                            </li>
                                                                                    <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/4dbec4e0d7474e4aa55e19b5d35085ea.jpg" alt=""/>
                                                                            </li>
                                                                            
                                                                </ul>
                                                            </a>
                                                    </section>
                                                    <section class="price-column  price-with-finance
                                                    ">

                                                            <a class="js-click-handler listing-fpa-link listings-price-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " href="/classified/advert/201909252598088?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" rel="nofollow">

                                                                    <div data-label="search appearance click" class="vehicle-price">£39,900</div>
                                                            </a>


                                                                    <div class="finance-price-section">
                                                                        <a href="/classified/advert/201909252598088?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" rel="nofollow" class="finance-price">
                                                                            &pound;727
                                                                        </a>
                                                                        <p class="finance-label">per month (PCP)</p>

                                                                        <div tabindex="0" role="button" aria-label="Open finance example" class="finance-info js-finance-lightbox-trigger tracking-standard-link">Finance example</div>

                                                                        <div class="finance-details results-lightbox">

                                                                            <div>
                                                                                <span role="button" tabindex="0" aria-label="Close finance example" class="results-lightbox-close js-writeoff-lightbox-close">&#x2715;</span>
                                                                                <h3 class="results-lightbox-title">PCP representative example</h3>
                                                                            </div>

                                                                            <table class="finance-details__table">
                                                                                <tr>
                                                                                    <td>Finance type</td>
                                                                                    <td>PCP</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Monthly payments</td>
                                                                                    <td>£726.63</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Term</td>
                                                                                    <td>48 months</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Contract Length</td>
                                                                                    <td>48 months</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>
                                                                                                Cash price
                                                                                    </td>
                                                                                    <td>£39,900.00</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Cash deposit</td>
                                                                                    <td>£1,000.00</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Total amount of credit</td>
                                                                                    <td>£38,900.00</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Total amount payable</td>
                                                                                    <td>£46,804.57</td>
                                                                                </tr>

                                                                                <tr>
                                                                                    <td>Representative APR</td>
                                                                                    <td>6.9&#37;</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Total charges payable</td>
                                                                                    <td>£6,904.57</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Fixed rate of interest pa</td>
                                                                                    <td>6.89&#37;</td>
                                                                                </tr>
                                                                                    <tr>
                                                                                        <td>Optional final payment</td>
                                                                                        <td>£11,652.96</td>
                                                                                    </tr>
                                                                            </table>
                                                                            <div class="finance-details__product-info">
                                                                                <p class="finance-details__product-info__title">What is PCP?</p>

                                                                                                                    <p>Personal contract purchase (PCP) is a flexible way to finance a vehicle. You pay an initial deposit followed by monthly payments (including interest), then at the end of the agreement you have three options:</p>

                                                                                                                    <ul class="atc-list">
                                                                                                                                                <li class="atc-list__item">Buy the vehicle by paying the optional final payment (also known as balloon payment) and the optional purchase fee.</li>
                                                                                                                                                                        <li class="atc-list__item">Return the vehicle to the dealer and walk away. There may be additional charges if it’s damaged or you’ve exceeded the mileage allowance.</li>
                                                                                                                                                                        <li class="atc-list__item">Get a new vehicle on another PCP deal. If the vehicle is worth more than the optional final payment, you can use it as a deposit for your next vehicle.</li>
                                                                                                                                                
                                                                                                                    </ul>
                                                                                                                
                                                                                            
                                                                                <a href="/car-finance/guides/car-finance-explained" target="_blank" rel="noopener noreferrer">Learn more about finance</a>
                                                                            </div>
                                                                        </div>
                                                                    </div>

                                                                        <div class="vehicle-seller-logo  long-logo ">
                                                                                    <span class="listing-approved-logo"><img src="/images/approved/search/porsche.gif" alt="Advertiser Logo Porsche Centre Perth"/></span>
                                                                            <img src="https://dealerlogo.atcdn.co.uk/at2/adbranding/10013602/images/searchlogo.gif" alt="Advertiser Logo Porsche Centre Perth"/>
                                                                        </div>


                                                            </section>
                                                </article>
                                                <ul class="action-links">
                                                    <li>
                                                        <a href="https://partnerships-motor-gateway.comparethemarket.com/product/car/start?vrn=AAAABy43hvA2GgEz&imageurl=https%3A%2F%2Fm.atcdn.co.uk%2Fa%2Fmedia%2Fb9ba0685b6bc4003935d79664e703837.jpg&affclie=DK79&value=39900&numSeats=4&driveSide=Unlisted&advertId=201909252598088" rel="noopener noreferrer nofollow"
                                                           class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-insurance-get-quote-initiation" target="_blank">Get an insurance quote</a>
                                                    </li>

                                                        <li>
                                                            <a href="/classified/advert/201909252598088?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2#check-history" rel="noopener noreferrer nofollow"
                                                               class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-vehicle-check-initiation">Check its history</a>
                                                        </li>
                                                </ul>
                                        </li>





                            <li class="search-page__result"
                                id="201906259399630"

                                data-search-results-advert-card
                                data-advert-id="201906259399630"

                                data-is-group-stock="false"
                                data-is-national-stock-advert="false"
                                data-is-allocated-stock="false"
                                data-is-virtual-stock="false"
                                data-is-network-stock="false"

                                data-image-count="20"
                                data-is-manufacturer-approved="false"
                                data-has-finance="true"
                                data-is-franchise-approved="false"
                                data-good-great-value="noanalysis"
                                data-distance-value="14 miles"
                                data-condition-value=""
                            >
                                    <article
                                            data-standout-type=""
                                            class=" search-listing
                                     sso-listing 

                                     no-logo ">
                                        <section class="content-column">
                                                <figure class="listing-main-image">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa  href="/classified/advert/201906259399630?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">

                                                    <div class="listing-image-count" data-label="search appearance click ">
                                                        <i data-label="search appearance click " class="listing-image-icon">
                                                            <svg>
                                                                <use xlink:href="/templates/_generated/svg_icons/search-listings.svg#icon-camera"></use>
                                                            </svg>
                                                        </i> 20


                                                        <!--replace with hasSpin-->
                                                    </div>

                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w260h196pd8d8d8/47fda12d2609441a8829fd3a112cb51f.jpg"/>
                                                    </a>
                                                </figure>
                                            <div class="information-container">
                                                <h2 class="listing-title title-wrap">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click "  href="/classified/advert/201906259399630?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">Porsche Panamera 3.0 TD V6 Tiptronic 5dr</a>
                                                </h2>
                                                <p class="listing-attention-grabber ">1 owner, full PSH,&pound; 12k extras</p>
                                                <ul class="listing-key-specs ">


                                                                <li>2014 (14 reg)</li>
                                                                
                                                                <li>Hatchback</li>
                                                                
                                                                <li>29,500 miles</li>
                                                                
                                                                <li>3.0L</li>
                                                                
                                                                <li>300bhp</li>
                                                                
                                                                <li>Automatic</li>
                                                                
                                                                <li>Diesel</li>
                                                                

                                                    </ul>
                                                 <ul class="listing-extra-detail">



                                                 </ul>


                                                        <p class="listing-description">One Owner from new, full Porsche service history, cost new circa &pound;75k, saving &hellip;</p>
                                                <div class="seller-info ">
                                                    <div class="seller-type ">
                                                                    Private seller
                                                    </div>


                                                                <div class="seller-location">
                                                <span class="seller-town">radlett</span> - 
                                                                        14 miles away
                                                                </div>
                                                </div>
                                            </div>
                                                <a class=" js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa href="/classified/advert/201906259399630?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >
                                                    <ul class="listing__thumbnails">
                                                                <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/43dfb22e45a741768ad51d09b9f3bdf8.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/6f7e90cc03df49a5acb2bf40df4723d8.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/c874a5488ecb4ab0b2f77d107d737ea3.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/ee78565172fe4895a41dab382611b7b9.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/c9ce916d05ca4ec884687a361375b79e.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/9776a99876d445d9af1597c8ba20303f.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/63c1f12d929e4eaabb9f6a04616c935f.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/85f553ef7c394053a4d1c3b7cfe23cbf.jpg" alt=""/>
                                                                </li>
                                                                
                                                    </ul>
                                                </a>
                                        </section>
                                        <section class="price-column  price-with-finance
                                        ">

                                                <a class="js-click-handler listing-fpa-link listings-price-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " href="/classified/advert/201906259399630?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >

                                                        <div data-label="search appearance click" class="vehicle-price">£29,995</div>
                                                </a>


                                                        <div class="finance-price-section">
                                                            <a href="/classified/advert/201906259399630?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2"  class="finance-price">
                                                                &pound;857
                                                            </a>
                                                            <p class="finance-label">per month (HP)</p>

                                                            <div tabindex="0" role="button" aria-label="Open finance example" class="finance-info js-finance-lightbox-trigger tracking-standard-link">Finance example</div>

                                                            <div class="finance-details results-lightbox">

                                                                <div>
                                                                    <span role="button" tabindex="0" aria-label="Close finance example" class="results-lightbox-close js-writeoff-lightbox-close">&#x2715;</span>
                                                                    <h3 class="results-lightbox-title">HP representative example</h3>
                                                                </div>

                                                                <table class="finance-details__table">
                                                                    <tr>
                                                                        <td>Finance type</td>
                                                                        <td>HP</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Monthly payments</td>
                                                                        <td>£856.08</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Term</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Contract Length</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>
                                                                                    Cash price
                                                                        </td>
                                                                        <td>£29,995.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Cash deposit</td>
                                                                        <td>£1,000.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount of credit</td>
                                                                        <td>£28,995.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount payable</td>
                                                                        <td>£42,092.84</td>
                                                                    </tr>

                                                                    <tr>
                                                                        <td>Representative APR</td>
                                                                        <td>19.9&#37;</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total charges payable</td>
                                                                        <td>£12,097.84</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Fixed rate of interest pa</td>
                                                                        <td>10.43&#37;</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Option to purchase fee</td>
                                                                        <td>£1.00</td>
                                                                    </tr>
                                                                </table>
                                                                <div class="finance-details__product-info">
                                                                    <p class="finance-details__product-info__title">What is HP?</p>

                                                                                                        <p>Hire purchase (HP) is an affordable way to buy a vehicle as it allows you to pay a deposit, and then make monthly payments to pay off the remaining amount.</p>

                                                                                                                        <p>You’ll be the registered keeper of the vehicle and responsible for insurance, servicing and maintenance, but the finance company will be the legal owner of the vehicle until the outstanding finance (including interest and fees) is paid off.</p>

                                                                                                    
                                                                                
                                                                    <a href="/car-finance/guides/car-finance-explained" target="_blank" rel="noopener noreferrer">Learn more about finance</a>
                                                                </div>
                                                            </div>
                                                        </div>


                                                </section>
                                    </article>
                                    <ul class="action-links">
                                        <li>
                                            <a href="https://partnerships-motor-gateway.comparethemarket.com/product/car/start?vrn=AAAABypZi%2BDA77lI&imageurl=https%3A%2F%2Fm.atcdn.co.uk%2Fa%2Fmedia%2F47fda12d2609441a8829fd3a112cb51f.jpg&affclie=DK78&value=29995&numSeats=4&driveSide=Unlisted&advertId=201906259399630" rel="noopener noreferrer nofollow"
                                               class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-insurance-get-quote-initiation" target="_blank">Get an insurance quote</a>
                                        </li>

                                            <li>
                                                <a href="/classified/advert/201906259399630?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2#check-history" rel="noopener noreferrer nofollow"
                                                   class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-vehicle-check-initiation">Check its history</a>
                                            </li>
                                    </ul>
                            </li>




                        



                            <li class="search-page__result"
                                id="201909212476563"

                                data-search-results-advert-card
                                data-advert-id="201909212476563"

                                data-is-group-stock="false"
                                data-is-national-stock-advert="false"
                                data-is-allocated-stock="false"
                                data-is-virtual-stock="false"
                                data-is-network-stock="false"

                                data-image-count="16"
                                data-is-manufacturer-approved="false"
                                data-has-finance="true"
                                data-is-franchise-approved="false"
                                data-good-great-value="noanalysis"
                                data-distance-value="145 miles"
                                data-condition-value=""
                            >
                                    <article
                                            data-standout-type=""
                                            class=" search-listing
                                     sso-listing 

                                     no-logo ">
                                        <section class="content-column">
                                                <figure class="listing-main-image">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa  href="/classified/advert/201909212476563?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">

                                                    <div class="listing-image-count" data-label="search appearance click ">
                                                        <i data-label="search appearance click " class="listing-image-icon">
                                                            <svg>
                                                                <use xlink:href="/templates/_generated/svg_icons/search-listings.svg#icon-camera"></use>
                                                            </svg>
                                                        </i> 16


                                                        <!--replace with hasSpin-->
                                                    </div>

                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w260h196pd8d8d8/47649afef1e5401facf6c9d57bac295d.jpg"/>
                                                    </a>
                                                </figure>
                                            <div class="information-container">
                                                <h2 class="listing-title title-wrap">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click "  href="/classified/advert/201909212476563?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">Porsche Panamera 3.6 V6 4 PDK AWD 5dr</a>
                                                </h2>
                                                <p class="listing-attention-grabber "></p>
                                                <ul class="listing-key-specs ">


                                                                <li>2010 (60 reg)</li>
                                                                
                                                                <li>Hatchback</li>
                                                                
                                                                <li>112,000 miles</li>
                                                                
                                                                <li>3.6L</li>
                                                                
                                                                <li>300bhp</li>
                                                                
                                                                <li>Automatic</li>
                                                                
                                                                <li>Petrol</li>
                                                                

                                                    </ul>
                                                 <ul class="listing-extra-detail">



                                                 </ul>


                                                        <p class="listing-description">2010 Porsche Panamera 3.0 V6, in Metallic Black with Matching 20&quot; Panamera Turbo &hellip;</p>
                                                <div class="seller-info ">
                                                    <div class="seller-type ">
                                                                    Private seller
                                                    </div>


                                                                <div class="seller-location">
                                                <span class="seller-town">honiton</span> - 
                                                                        145 miles away
                                                                </div>
                                                </div>
                                            </div>
                                                <a class=" js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa href="/classified/advert/201909212476563?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >
                                                    <ul class="listing__thumbnails">
                                                                <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/700296f1d9ec48a08f230cb92336fd8a.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/702f99ce7685495d866c62c037eadf6e.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/789d600745bf48f599f49c73693c5712.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/f524d073d6c74c81b8b88fe3a1c919f4.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/d99d8ef391904e6485466b6a8ace9c75.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/b464e59bbeea49c7a9924b3a2e3f6a3d.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/400bb531a866499c97431de49f7f6ff3.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/64ffb98ebf044fbaa4f833c473a9fc5f.jpg" alt=""/>
                                                                </li>
                                                                
                                                    </ul>
                                                </a>
                                        </section>
                                        <section class="price-column  price-with-finance
                                        ">

                                                <a class="js-click-handler listing-fpa-link listings-price-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " href="/classified/advert/201909212476563?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >

                                                        <div data-label="search appearance click" class="vehicle-price">£17,995</div>
                                                </a>


                                                        <div class="finance-price-section">
                                                            <a href="/classified/advert/201909212476563?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2"  class="finance-price">
                                                                &pound;502
                                                            </a>
                                                            <p class="finance-label">per month (HP)</p>

                                                            <div tabindex="0" role="button" aria-label="Open finance example" class="finance-info js-finance-lightbox-trigger tracking-standard-link">Finance example</div>

                                                            <div class="finance-details results-lightbox">

                                                                <div>
                                                                    <span role="button" tabindex="0" aria-label="Close finance example" class="results-lightbox-close js-writeoff-lightbox-close">&#x2715;</span>
                                                                    <h3 class="results-lightbox-title">HP representative example</h3>
                                                                </div>

                                                                <table class="finance-details__table">
                                                                    <tr>
                                                                        <td>Finance type</td>
                                                                        <td>HP</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Monthly payments</td>
                                                                        <td>£501.78</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Term</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Contract Length</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>
                                                                                    Cash price
                                                                        </td>
                                                                        <td>£17,995.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Cash deposit</td>
                                                                        <td>£1,000.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount of credit</td>
                                                                        <td>£16,995.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount payable</td>
                                                                        <td>£25,086.44</td>
                                                                    </tr>

                                                                    <tr>
                                                                        <td>Representative APR</td>
                                                                        <td>19.9&#37;</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total charges payable</td>
                                                                        <td>£7,091.44</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Fixed rate of interest pa</td>
                                                                        <td>10.43&#37;</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Option to purchase fee</td>
                                                                        <td>£1.00</td>
                                                                    </tr>
                                                                </table>
                                                                <div class="finance-details__product-info">
                                                                    <p class="finance-details__product-info__title">What is HP?</p>

                                                                                                        <p>Hire purchase (HP) is an affordable way to buy a vehicle as it allows you to pay a deposit, and then make monthly payments to pay off the remaining amount.</p>

                                                                                                                        <p>You’ll be the registered keeper of the vehicle and responsible for insurance, servicing and maintenance, but the finance company will be the legal owner of the vehicle until the outstanding finance (including interest and fees) is paid off.</p>

                                                                                                    
                                                                                
                                                                    <a href="/car-finance/guides/car-finance-explained" target="_blank" rel="noopener noreferrer">Learn more about finance</a>
                                                                </div>
                                                            </div>
                                                        </div>


                                                </section>
                                    </article>
                                    <ul class="action-links">
                                        <li>
                                            <a href="https://partnerships-motor-gateway.comparethemarket.com/product/car/start?vrn=AAAABy2Y7zdCJWfN&imageurl=https%3A%2F%2Fm.atcdn.co.uk%2Fa%2Fmedia%2F47649afef1e5401facf6c9d57bac295d.jpg&affclie=DK78&value=17995&numSeats=4&driveSide=Unlisted&advertId=201909212476563" rel="noopener noreferrer nofollow"
                                               class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-insurance-get-quote-initiation" target="_blank">Get an insurance quote</a>
                                        </li>

                                            <li>
                                                <a href="/classified/advert/201909212476563?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2#check-history" rel="noopener noreferrer nofollow"
                                                   class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-vehicle-check-initiation">Check its history</a>
                                            </li>
                                    </ul>
                            </li>




                        



                            <li class="search-page__result"
                                id="201908271568643"

                                data-search-results-advert-card
                                data-advert-id="201908271568643"

                                data-is-group-stock="false"
                                data-is-national-stock-advert="false"
                                data-is-allocated-stock="false"
                                data-is-virtual-stock="false"
                                data-is-network-stock="false"

                                data-image-count="30"
                                data-is-manufacturer-approved="false"
                                data-has-finance="true"
                                data-is-franchise-approved="false"
                                data-good-great-value="noanalysis"
                                data-distance-value="74 miles"
                                data-condition-value=""
                            >
                                    <article
                                            data-standout-type=""
                                            class=" search-listing
                                     sso-listing 

                                    ">
                                        <section class="content-column">
                                                <figure class="listing-main-image">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa  href="/classified/advert/201908271568643?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">

                                                    <div class="listing-image-count" data-label="search appearance click ">
                                                        <i data-label="search appearance click " class="listing-image-icon">
                                                            <svg>
                                                                <use xlink:href="/templates/_generated/svg_icons/search-listings.svg#icon-camera"></use>
                                                            </svg>
                                                        </i> 30

                                                            <i data-label="search appearance click " class="listing-video-icon">
                                                                <svg>
                                                                    <use xlink:href="/templates/_generated/svg_icons/search-listings.svg#icon-video"></use>
                                                                </svg>
                                                            </i> Video

                                                        <!--replace with hasSpin-->
                                                    </div>

                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w260h196pd8d8d8/9ba3dbc799f94594ac7f0486fd5259f4.jpg"/>
                                                    </a>
                                                </figure>
                                            <div class="information-container">
                                                <h2 class="listing-title title-wrap">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click "  href="/classified/advert/201908271568643?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">Porsche Panamera 4.0 TD V8 4S PDK 4WD (s/s) 4dr</a>
                                                </h2>
                                                <p class="listing-attention-grabber ">21&quot;S, AIR SUSPENSION, PAN ROOF</p>
                                                <ul class="listing-key-specs ">


                                                                <li>2016 (66 reg)</li>
                                                                
                                                                <li>Hatchback</li>
                                                                
                                                                <li>53,067 miles</li>
                                                                
                                                                <li>4.0L</li>
                                                                
                                                                <li>415bhp</li>
                                                                
                                                                <li>Automatic</li>
                                                                
                                                                <li>Diesel</li>
                                                                

                                                    </ul>
                                                 <ul class="listing-extra-detail">



                                                 </ul>


                                                        <p class="listing-description">REAR AXLE STEERING, LED HEADLIGHTS, SOFT CLOSE, BOSE PREMIUM SOUND, REVERSING &hellip;</p>
                                                <div class="seller-info seller-profile-link">
                                                    <div class="seller-type  trade-seller">
                                                                    Trade seller - <a href="/dealers/gloucestershire/moreton-in-marsh/john-holland-at-rennsport-10017987" >See all 9 cars</a>
                                                    </div>


                                                                <div class="seller-location">
                                                <span class="seller-town">moreton-in-marsh</span> - 
                                                                        74 miles away
                                                                </div>
                                                </div>
                                            </div>
                                                <a class=" js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa href="/classified/advert/201908271568643?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >
                                                    <ul class="listing__thumbnails">
                                                                <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/6fd47a50dce94f7aa53a579ac8b33333.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/51bcc85b6c7a45e58eebb4b41f5e5528.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/4428324690cb4937a98920e71a8570ad.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/20687e2f3f9c437cad9b257aa06fa51f.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/c11bad3ed3dd4a14b5bc5bd1e76c01d2.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/74840632ae7540d4932fa1aaa413754a.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/64d304dee7014733990a4062a9cd5305.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/e39a14c089994cc28ed08c7a40e830f7.jpg" alt=""/>
                                                                </li>
                                                                
                                                    </ul>
                                                </a>
                                        </section>
                                        <section class="price-column  price-with-finance
                                        ">

                                                <a class="js-click-handler listing-fpa-link listings-price-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " href="/classified/advert/201908271568643?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >

                                                        <div data-label="search appearance click" class="vehicle-price">£57,895</div>
                                                </a>


                                                        <div class="finance-price-section">
                                                            <a href="/classified/advert/201908271568643?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2"  class="finance-price">
                                                                &pound;1006
                                                            </a>
                                                            <p class="finance-label">per month (PCP)</p>

                                                            <div tabindex="0" role="button" aria-label="Open finance example" class="finance-info js-finance-lightbox-trigger tracking-standard-link">Finance example</div>

                                                            <div class="finance-details results-lightbox">

                                                                <div>
                                                                    <span role="button" tabindex="0" aria-label="Close finance example" class="results-lightbox-close js-writeoff-lightbox-close">&#x2715;</span>
                                                                    <h3 class="results-lightbox-title">PCP representative example</h3>
                                                                </div>

                                                                <table class="finance-details__table">
                                                                    <tr>
                                                                        <td>Finance type</td>
                                                                        <td>PCP</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Monthly payments</td>
                                                                        <td>£1,005.18</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Term</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Contract Length</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>
                                                                                    Cash price
                                                                        </td>
                                                                        <td>£57,895.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Cash deposit</td>
                                                                        <td>£1,000.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount of credit</td>
                                                                        <td>£56,895.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount payable</td>
                                                                        <td>£71,973.71</td>
                                                                    </tr>

                                                                    <tr>
                                                                        <td>Representative APR</td>
                                                                        <td>8.9&#37;</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total charges payable</td>
                                                                        <td>£14,078.71</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Fixed rate of interest pa</td>
                                                                        <td>8.9&#37;</td>
                                                                    </tr>
                                                                        <tr>
                                                                            <td>Optional final payment</td>
                                                                            <td>£23,730.25</td>
                                                                        </tr>
                                                                </table>
                                                                <div class="finance-details__product-info">
                                                                    <p class="finance-details__product-info__title">What is PCP?</p>

                                                                                                        <p>Personal contract purchase (PCP) is a flexible way to finance a vehicle. You pay an initial deposit followed by monthly payments (including interest), then at the end of the agreement you have three options:</p>

                                                                                                        <ul class="atc-list">
                                                                                                                                    <li class="atc-list__item">Buy the vehicle by paying the optional final payment (also known as balloon payment) and the optional purchase fee.</li>
                                                                                                                                                            <li class="atc-list__item">Return the vehicle to the dealer and walk away. There may be additional charges if it’s damaged or you’ve exceeded the mileage allowance.</li>
                                                                                                                                                            <li class="atc-list__item">Get a new vehicle on another PCP deal. If the vehicle is worth more than the optional final payment, you can use it as a deposit for your next vehicle.</li>
                                                                                                                                    
                                                                                                        </ul>
                                                                                                    
                                                                                
                                                                    <a href="/car-finance/guides/car-finance-explained" target="_blank" rel="noopener noreferrer">Learn more about finance</a>
                                                                </div>
                                                            </div>
                                                        </div>

                                                            <div class="vehicle-seller-logo  long-logo ">
                                                                <img src="https://dealerlogo.atcdn.co.uk/at2/adbranding/10017987/images/searchlogo.gif" alt="Advertiser Logo John Holland at Rennsport"/>
                                                            </div>


                                                </section>
                                    </article>
                                    <ul class="action-links">
                                        <li>
                                            <a href="https://partnerships-motor-gateway.comparethemarket.com/product/car/start?vrn=AAAAByNw0h21zfIo&imageurl=https%3A%2F%2Fm.atcdn.co.uk%2Fa%2Fmedia%2F9ba3dbc799f94594ac7f0486fd5259f4.jpg&affclie=DK79&value=57895&numSeats=4&driveSide=Unlisted&advertId=201908271568643" rel="noopener noreferrer nofollow"
                                               class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-insurance-get-quote-initiation" target="_blank">Get an insurance quote</a>
                                        </li>

                                            <li>
                                                <a href="/classified/advert/201908271568643?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2#check-history" rel="noopener noreferrer nofollow"
                                                   class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-vehicle-check-initiation">Check its history</a>
                                            </li>
                                    </ul>
                            </li>




                        

                                <li>
                                    <div id="gpt-slot-6" class="banner--4th-position listing-outer-shadow" data-search-results-advert-card data-is-google-insearch-ad="true"></div>
                                </li>


                            <li class="search-page__result"
                                id="201906289507830"

                                data-search-results-advert-card
                                data-advert-id="201906289507830"

                                data-is-group-stock="false"
                                data-is-national-stock-advert="false"
                                data-is-allocated-stock="false"
                                data-is-virtual-stock="false"
                                data-is-network-stock="false"

                                data-image-count="15"
                                data-is-manufacturer-approved="false"
                                data-has-finance="true"
                                data-is-franchise-approved="false"
                                data-good-great-value="noanalysis"
                                data-distance-value="108 miles"
                                data-condition-value=""
                            >
                                    <article
                                            data-standout-type=""
                                            class=" search-listing
                                     sso-listing 

                                     no-logo ">
                                        <section class="content-column">
                                                <figure class="listing-main-image">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa  href="/classified/advert/201906289507830?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">

                                                    <div class="listing-image-count" data-label="search appearance click ">
                                                        <i data-label="search appearance click " class="listing-image-icon">
                                                            <svg>
                                                                <use xlink:href="/templates/_generated/svg_icons/search-listings.svg#icon-camera"></use>
                                                            </svg>
                                                        </i> 15


                                                        <!--replace with hasSpin-->
                                                    </div>

                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w260h196pd8d8d8/6ec8bf88b7ab4f679678357efc9cb953.jpg"/>
                                                    </a>
                                                </figure>
                                            <div class="information-container">
                                                <h2 class="listing-title title-wrap">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click "  href="/classified/advert/201906289507830?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">Porsche Panamera 3.0 TD V6 Platinum Edition Tiptronic S 5dr</a>
                                                </h2>
                                                <p class="listing-attention-grabber ">55k miles, FSH, may px</p>
                                                <ul class="listing-key-specs ">


                                                                <li>2013 (13 reg)</li>
                                                                
                                                                <li>Hatchback</li>
                                                                
                                                                <li>55,850 miles</li>
                                                                
                                                                <li>3.0L</li>
                                                                
                                                                <li>250bhp</li>
                                                                
                                                                <li>Automatic</li>
                                                                
                                                                <li>Diesel</li>
                                                                

                                                    </ul>
                                                 <ul class="listing-extra-detail">



                                                 </ul>


                                                        <p class="listing-description">1 previous owner, Platinum edition with lots of optional extras. Just mot'd, had &hellip;</p>
                                                <div class="seller-info ">
                                                    <div class="seller-type ">
                                                                    Private seller
                                                    </div>


                                                                <div class="seller-location">
                                                <span class="seller-town">dudley</span> - 
                                                                        108 miles away
                                                                </div>
                                                </div>
                                            </div>
                                                <a class=" js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa href="/classified/advert/201906289507830?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >
                                                    <ul class="listing__thumbnails">
                                                                <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/6e00f9ec98834999b74121bc73e07a95.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/93398a259b654a9a9e79494572061e45.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/ca3500c64512490da3684cd86347bb55.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/0224792b864f482e8daafcf0ef20b6ef.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/c3312aefd0ac46b6acec5995dba76805.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/d43cae0763294fcc8915d08b5cee0999.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/058e9ad0f72c4dc19b797b8ca624214d.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/9954ed524fce481db3dac6633e93d829.jpg" alt=""/>
                                                                </li>
                                                                
                                                    </ul>
                                                </a>
                                        </section>
                                        <section class="price-column  price-with-finance
                                        ">

                                                <a class="js-click-handler listing-fpa-link listings-price-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " href="/classified/advert/201906289507830?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >

                                                        <div data-label="search appearance click" class="vehicle-price">£25,000</div>
                                                </a>


                                                        <div class="finance-price-section">
                                                            <a href="/classified/advert/201906289507830?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2"  class="finance-price">
                                                                &pound;709
                                                            </a>
                                                            <p class="finance-label">per month (HP)</p>

                                                            <div tabindex="0" role="button" aria-label="Open finance example" class="finance-info js-finance-lightbox-trigger tracking-standard-link">Finance example</div>

                                                            <div class="finance-details results-lightbox">

                                                                <div>
                                                                    <span role="button" tabindex="0" aria-label="Close finance example" class="results-lightbox-close js-writeoff-lightbox-close">&#x2715;</span>
                                                                    <h3 class="results-lightbox-title">HP representative example</h3>
                                                                </div>

                                                                <table class="finance-details__table">
                                                                    <tr>
                                                                        <td>Finance type</td>
                                                                        <td>HP</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Monthly payments</td>
                                                                        <td>£708.60</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Term</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Contract Length</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>
                                                                                    Cash price
                                                                        </td>
                                                                        <td>£25,000.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Cash deposit</td>
                                                                        <td>£1,000.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount of credit</td>
                                                                        <td>£24,000.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount payable</td>
                                                                        <td>£35,013.80</td>
                                                                    </tr>

                                                                    <tr>
                                                                        <td>Representative APR</td>
                                                                        <td>19.9&#37;</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total charges payable</td>
                                                                        <td>£10,013.80</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Fixed rate of interest pa</td>
                                                                        <td>10.43&#37;</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Option to purchase fee</td>
                                                                        <td>£1.00</td>
                                                                    </tr>
                                                                </table>
                                                                <div class="finance-details__product-info">
                                                                    <p class="finance-details__product-info__title">What is HP?</p>

                                                                                                        <p>Hire purchase (HP) is an affordable way to buy a vehicle as it allows you to pay a deposit, and then make monthly payments to pay off the remaining amount.</p>

                                                                                                                        <p>You’ll be the registered keeper of the vehicle and responsible for insurance, servicing and maintenance, but the finance company will be the legal owner of the vehicle until the outstanding finance (including interest and fees) is paid off.</p>

                                                                                                    
                                                                                
                                                                    <a href="/car-finance/guides/car-finance-explained" target="_blank" rel="noopener noreferrer">Learn more about finance</a>
                                                                </div>
                                                            </div>
                                                        </div>


                                                </section>
                                    </article>
                                    <ul class="action-links">
                                        <li>
                                            <a href="https://partnerships-motor-gateway.comparethemarket.com/product/car/start?vrn=AAAAB2CF9N4Q54LM&imageurl=https%3A%2F%2Fm.atcdn.co.uk%2Fa%2Fmedia%2F6ec8bf88b7ab4f679678357efc9cb953.jpg&affclie=DK78&value=25000&numSeats=4&driveSide=Unlisted&advertId=201906289507830" rel="noopener noreferrer nofollow"
                                               class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-insurance-get-quote-initiation" target="_blank">Get an insurance quote</a>
                                        </li>

                                            <li>
                                                <a href="/classified/advert/201906289507830?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2#check-history" rel="noopener noreferrer nofollow"
                                                   class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-vehicle-check-initiation">Check its history</a>
                                            </li>
                                    </ul>
                            </li>




                        



                            <li class="search-page__result"
                                id="201908050811645"

                                data-search-results-advert-card
                                data-advert-id="201908050811645"

                                data-is-group-stock="false"
                                data-is-national-stock-advert="false"
                                data-is-allocated-stock="false"
                                data-is-virtual-stock="false"
                                data-is-network-stock="false"

                                data-image-count="51"
                                data-is-manufacturer-approved="false"
                                data-has-finance="true"
                                data-is-franchise-approved="false"
                                data-good-great-value="great"
                                data-distance-value="27 miles"
                                data-condition-value=""
                            >
                                    <article
                                            data-standout-type=""
                                            class=" search-listing
                                     sso-listing 

                                    ">
                                        <section class="content-column">
                                                <figure class="listing-main-image">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa  href="/classified/advert/201908050811645?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">

                                                    <div class="listing-image-count" data-label="search appearance click ">
                                                        <i data-label="search appearance click " class="listing-image-icon">
                                                            <svg>
                                                                <use xlink:href="/templates/_generated/svg_icons/search-listings.svg#icon-camera"></use>
                                                            </svg>
                                                        </i> 51


                                                        <!--replace with hasSpin-->
                                                    </div>

                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w260h196pd8d8d8/b79eab1ee2eb418c9672999865ab1e63.jpg"/>
                                                    </a>
                                                </figure>
                                            <div class="information-container">
                                                <h2 class="listing-title title-wrap">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click "  href="/classified/advert/201908050811645?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">Porsche Panamera 3.0 V6 S E-Hybrid 4dr Tiptronic S</a>
                                                </h2>
                                                <p class="listing-attention-grabber ">&pound;12K OPTIONS | BOSE | EURO 6</p>
                                                <ul class="listing-key-specs ">


                                                                <li>2016 (66 reg)</li>
                                                                
                                                                <li>Hatchback</li>
                                                                
                                                                <li>27,000 miles</li>
                                                                
                                                                <li>3.0L</li>
                                                                
                                                                <li>333bhp</li>
                                                                
                                                                <li>Automatic</li>
                                                                
                                                                <li>Hybrid – Petrol/Electric Plug-in</li>
                                                                

                                                    </ul>
                                                 <ul class="listing-extra-detail">



                                                 </ul>


                                                        <p class="listing-description">Kent Motor Cars are excited to offer this phenomenal 2016 Porsche Panamera S. &hellip;</p>
                                                <div class="seller-info seller-profile-link">
                                                    <div class="seller-type  trade-seller">
                                                                    Trade seller - <a href="/dealers/kent/sevenoaks/kent-motor-cars-10005875" >See all 94 cars</a>
                                                    </div>


                                                                <div class="seller-location">
                                                <span class="seller-town">sevenoaks</span> - 
                                                                        27 miles away
                                                                </div>
                                                </div>
                                            </div>
                                                <a class=" js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa href="/classified/advert/201908050811645?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >
                                                    <ul class="listing__thumbnails">
                                                                <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/626e104566714a2d82333cf908223b0c.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/45499dd9cd334bc284e99f30a725bd2a.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/a2018ee83be94b3684f8faa45315a17e.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/8d938e8a607b4b8484b12b8c50070454.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/1acc628000aa425ca3a14ff3f2e2d523.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/217e7b0b5e3b4e8c9904e61f08d8aeb5.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/98b444be0bb84b51a9efe355b0bbbcf1.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/1f49927efeec46bb851e7ecd67cceea3.jpg" alt=""/>
                                                                </li>
                                                                
                                                    </ul>
                                                </a>
                                        </section>
                                        <section class="price-column  price-with-finance
                                         price-with-pi ">

                                                <a class="js-click-handler listing-fpa-link listings-price-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " href="/classified/advert/201908050811645?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >

                                                        <div data-label="search appearance click" class="vehicle-price">£49,945</div>
                                                </a>

                                                <div class="js-tooltip">
                                                    <span class="search-result__good-great-value pi-indicator js-tooltip-trigger">great Price</span>
                                                    <div class="search-result__valueIndicatorTooltip">
                                                        <div class="tooltip  tooltip__arrow--upRight js-tooltip-window">
                                                            <div class="tooltip-content">
                                                                <h3 class="search-result__valueIndicatorTitle">Why is this car a great price?</h3>
                                                                <span>Auto Trader has price-checked this car against the market value for similar cars and identified it as a great price.</span>
                                                            </div>
                                                            <div class="tooltip-close js-close"></div>
                                                        </div>
                                                    </div>
                                                    <span class="search-result__pi-based-on">Based on similar cars</span>
                                                </div>

                                                        <div class="finance-price-section">
                                                            <a href="/classified/advert/201908050811645?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2"  class="finance-price">
                                                                &pound;935
                                                            </a>
                                                            <p class="finance-label">per month (PCP)</p>

                                                            <div tabindex="0" role="button" aria-label="Open finance example" class="finance-info js-finance-lightbox-trigger tracking-standard-link">Finance example</div>

                                                            <div class="finance-details results-lightbox">

                                                                <div>
                                                                    <span role="button" tabindex="0" aria-label="Close finance example" class="results-lightbox-close js-writeoff-lightbox-close">&#x2715;</span>
                                                                    <h3 class="results-lightbox-title">PCP representative example</h3>
                                                                </div>

                                                                <table class="finance-details__table">
                                                                    <tr>
                                                                        <td>Finance type</td>
                                                                        <td>PCP</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Monthly payments</td>
                                                                        <td>£934.22</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Term</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Contract Length</td>
                                                                        <td>49 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>
                                                                                    Cash price
                                                                        </td>
                                                                        <td>£49,945.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Cash deposit</td>
                                                                        <td>£1,000.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount of credit</td>
                                                                        <td>£48,945.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount payable</td>
                                                                        <td>£63,119.81</td>
                                                                    </tr>

                                                                    <tr>
                                                                        <td>Representative APR</td>
                                                                        <td>9.9&#37;</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total charges payable</td>
                                                                        <td>£13,174.81</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Fixed rate of interest pa</td>
                                                                        <td>4.92&#37;</td>
                                                                    </tr>
                                                                        <tr>
                                                                            <td>Optional final payment</td>
                                                                            <td>£17,277.25</td>
                                                                        </tr>
                                                                    <tr>
                                                                        <td>Option to purchase fee</td>
                                                                        <td>£1.00</td>
                                                                    </tr>
                                                                </table>
                                                                <div class="finance-details__product-info">
                                                                    <p class="finance-details__product-info__title">What is PCP?</p>

                                                                                                        <p>Personal contract purchase (PCP) is a flexible way to finance a vehicle. You pay an initial deposit followed by monthly payments (including interest), then at the end of the agreement you have three options:</p>

                                                                                                        <ul class="atc-list">
                                                                                                                                    <li class="atc-list__item">Buy the vehicle by paying the optional final payment (also known as balloon payment) and the optional purchase fee.</li>
                                                                                                                                                            <li class="atc-list__item">Return the vehicle to the dealer and walk away. There may be additional charges if it’s damaged or you’ve exceeded the mileage allowance.</li>
                                                                                                                                                            <li class="atc-list__item">Get a new vehicle on another PCP deal. If the vehicle is worth more than the optional final payment, you can use it as a deposit for your next vehicle.</li>
                                                                                                                                    
                                                                                                        </ul>
                                                                                                    
                                                                                
                                                                    <a href="/car-finance/guides/car-finance-explained" target="_blank" rel="noopener noreferrer">Learn more about finance</a>
                                                                </div>
                                                            </div>
                                                        </div>

                                                            <div class="vehicle-seller-logo  long-logo ">
                                                                <img src="https://dealerlogo.atcdn.co.uk/at2/adbranding/10005875/images/searchlogo.gif" alt="Advertiser Logo Kent Motor Cars"/>
                                                            </div>


                                                </section>
                                    </article>
                                    <ul class="action-links">
                                        <li>
                                            <a href="https://partnerships-motor-gateway.comparethemarket.com/product/car/start?vrn=AAAABz7Q2hyYkLp8&imageurl=https%3A%2F%2Fm.atcdn.co.uk%2Fa%2Fmedia%2Fb79eab1ee2eb418c9672999865ab1e63.jpg&affclie=DK79&value=49945&numSeats=4&driveSide=Unlisted&advertId=201908050811645" rel="noopener noreferrer nofollow"
                                               class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-insurance-get-quote-initiation" target="_blank">Get an insurance quote</a>
                                        </li>

                                            <li>
                                                <a href="/classified/advert/201908050811645?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2#check-history" rel="noopener noreferrer nofollow"
                                                   class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-vehicle-check-initiation">Check its history</a>
                                            </li>
                                    </ul>
                            </li>




                        



                            <li class="search-page__result"
                                id="201904056639410"

                                data-search-results-advert-card
                                data-advert-id="201904056639410"

                                data-is-group-stock="false"
                                data-is-national-stock-advert="false"
                                data-is-allocated-stock="false"
                                data-is-virtual-stock="false"
                                data-is-network-stock="false"

                                data-image-count="50"
                                data-is-manufacturer-approved="false"
                                data-has-finance="true"
                                data-is-franchise-approved="false"
                                data-good-great-value="high"
                                data-distance-value="17 miles"
                                data-condition-value=""
                            >
                                    <article
                                            data-standout-type=""
                                            class=" search-listing
                                     sso-listing 

                                    ">
                                        <section class="content-column">
                                                <figure class="listing-main-image">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa  href="/classified/advert/201904056639410?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">

                                                    <div class="listing-image-count" data-label="search appearance click ">
                                                        <i data-label="search appearance click " class="listing-image-icon">
                                                            <svg>
                                                                <use xlink:href="/templates/_generated/svg_icons/search-listings.svg#icon-camera"></use>
                                                            </svg>
                                                        </i> 50


                                                        <!--replace with hasSpin-->
                                                    </div>

                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w260h196pd8d8d8/56ca81c0d7214792a77fb053c8cc7ea4.jpg"/>
                                                    </a>
                                                </figure>
                                            <div class="information-container">
                                                <h2 class="listing-title title-wrap">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click "  href="/classified/advert/201904056639410?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">Porsche Panamera 3.0 [300] V6 Diesel 4dr Tiptronic S</a>
                                                </h2>
                                                <p class="listing-attention-grabber ">Heated Seats | BOSE | Sat Nav</p>
                                                <ul class="listing-key-specs ">


                                                                <li>2014 (64 reg)</li>
                                                                
                                                                <li>Hatchback</li>
                                                                
                                                                <li>55,214 miles</li>
                                                                
                                                                <li>3.0L</li>
                                                                
                                                                <li>300bhp</li>
                                                                
                                                                <li>Automatic</li>
                                                                
                                                                <li>Diesel</li>
                                                                

                                                    </ul>
                                                 <ul class="listing-extra-detail">



                                                 </ul>


                                                        <p class="listing-description">Here at Prestige we are excited to present this beautiful 2014 Porsche Panamera &hellip;</p>
                                                <div class="seller-info seller-profile-link">
                                                    <div class="seller-type  trade-seller">
                                                                    Trade seller - <a href="/dealers/borough-of-bromley/orpington/prestige-cars-kent-678412" >See all 188 cars</a>
                                                    </div>


                                                                <div class="seller-location">
                                                <span class="seller-town">orpington</span> - 
                                                                        17 miles away
                                                                </div>
                                                </div>
                                            </div>
                                                <a class=" js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa href="/classified/advert/201904056639410?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >
                                                    <ul class="listing__thumbnails">
                                                                <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/4107acd4726d454caad3460abc284dc0.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/f681764db819427ba8973a4be5117ef6.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/e707d99b5c5b465790050f311bc790ec.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/b1fc6686706748b6b0ec9c1c34aef4a1.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/aee5cffe5f344556b102db13750fa15e.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/5cdc0531a171494981c766f4cf8aee4e.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/9fe2f7dfa19a4aa2b032b38f68e0c553.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/d07d10207fe84c35991c34bbfedd1211.jpg" alt=""/>
                                                                </li>
                                                                
                                                    </ul>
                                                </a>
                                        </section>
                                        <section class="price-column  price-with-finance
                                        ">

                                                <a class="js-click-handler listing-fpa-link listings-price-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " href="/classified/advert/201904056639410?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >

                                                        <div data-label="search appearance click" class="vehicle-price">£31,920</div>
                                                </a>


                                                        <div class="finance-price-section">
                                                            <a href="/classified/advert/201904056639410?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2"  class="finance-price">
                                                                &pound;579
                                                            </a>
                                                            <p class="finance-label">per month (PCP)</p>

                                                            <div tabindex="0" role="button" aria-label="Open finance example" class="finance-info js-finance-lightbox-trigger tracking-standard-link">Finance example</div>

                                                            <div class="finance-details results-lightbox">

                                                                <div>
                                                                    <span role="button" tabindex="0" aria-label="Close finance example" class="results-lightbox-close js-writeoff-lightbox-close">&#x2715;</span>
                                                                    <h3 class="results-lightbox-title">PCP representative example</h3>
                                                                </div>

                                                                <table class="finance-details__table">
                                                                    <tr>
                                                                        <td>Finance type</td>
                                                                        <td>PCP</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Monthly payments</td>
                                                                        <td>£578.12</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Term</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Contract Length</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>
                                                                                    Cash price
                                                                        </td>
                                                                        <td>£31,920.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Cash deposit</td>
                                                                        <td>£1,000.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount of credit</td>
                                                                        <td>£30,920.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount payable</td>
                                                                        <td>£38,177.30</td>
                                                                    </tr>

                                                                    <tr>
                                                                        <td>Representative APR</td>
                                                                        <td>7.7&#37;</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total charges payable</td>
                                                                        <td>£6,257.30</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Fixed rate of interest pa</td>
                                                                        <td>7.74&#37;</td>
                                                                    </tr>
                                                                        <tr>
                                                                            <td>Optional final payment</td>
                                                                            <td>£10,005.66</td>
                                                                        </tr>
                                                                </table>
                                                                <div class="finance-details__product-info">
                                                                    <p class="finance-details__product-info__title">What is PCP?</p>

                                                                                                        <p>Personal contract purchase (PCP) is a flexible way to finance a vehicle. You pay an initial deposit followed by monthly payments (including interest), then at the end of the agreement you have three options:</p>

                                                                                                        <ul class="atc-list">
                                                                                                                                    <li class="atc-list__item">Buy the vehicle by paying the optional final payment (also known as balloon payment) and the optional purchase fee.</li>
                                                                                                                                                            <li class="atc-list__item">Return the vehicle to the dealer and walk away. There may be additional charges if it’s damaged or you’ve exceeded the mileage allowance.</li>
                                                                                                                                                            <li class="atc-list__item">Get a new vehicle on another PCP deal. If the vehicle is worth more than the optional final payment, you can use it as a deposit for your next vehicle.</li>
                                                                                                                                    
                                                                                                        </ul>
                                                                                                    
                                                                                
                                                                    <a href="/car-finance/guides/car-finance-explained" target="_blank" rel="noopener noreferrer">Learn more about finance</a>
                                                                </div>
                                                            </div>
                                                        </div>

                                                            <div class="vehicle-seller-logo  long-logo ">
                                                                <img src="https://dealerlogo.atcdn.co.uk/at2/adbranding/678412/images/searchlogo.gif" alt="Advertiser Logo Prestige Cars Kent"/>
                                                            </div>


                                                </section>
                                    </article>
                                    <ul class="action-links">
                                        <li>
                                            <a href="https://partnerships-motor-gateway.comparethemarket.com/product/car/start?vrn=AAAAB%2F2VuX34g02M&imageurl=https%3A%2F%2Fm.atcdn.co.uk%2Fa%2Fmedia%2F56ca81c0d7214792a77fb053c8cc7ea4.jpg&affclie=DK79&value=31920&numSeats=4&driveSide=Unlisted&advertId=201904056639410" rel="noopener noreferrer nofollow"
                                               class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-insurance-get-quote-initiation" target="_blank">Get an insurance quote</a>
                                        </li>

                                            <li>
                                                <a href="/classified/advert/201904056639410?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2#check-history" rel="noopener noreferrer nofollow"
                                                   class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-vehicle-check-initiation">Check its history</a>
                                            </li>
                                    </ul>
                            </li>




                        


                                <li>
                                    <div id="gpt-slot-5" class="banner--7th-position listing-outer-shadow" data-search-results-advert-card data-is-google-insearch-ad="true"></div>
                                </li>

                            <li class="search-page__result"
                                id="201907250430713"

                                data-search-results-advert-card
                                data-advert-id="201907250430713"

                                data-is-group-stock="false"
                                data-is-national-stock-advert="false"
                                data-is-allocated-stock="false"
                                data-is-virtual-stock="false"
                                data-is-network-stock="false"

                                data-image-count="16"
                                data-is-manufacturer-approved="false"
                                data-has-finance="true"
                                data-is-franchise-approved="false"
                                data-good-great-value="great"
                                data-distance-value="101 miles"
                                data-condition-value=""
                            >
                                    <article
                                            data-standout-type=""
                                            class=" search-listing
                                     sso-listing 

                                    ">
                                        <section class="content-column">
                                                <figure class="listing-main-image">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa  href="/classified/advert/201907250430713?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">

                                                    <div class="listing-image-count" data-label="search appearance click ">
                                                        <i data-label="search appearance click " class="listing-image-icon">
                                                            <svg>
                                                                <use xlink:href="/templates/_generated/svg_icons/search-listings.svg#icon-camera"></use>
                                                            </svg>
                                                        </i> 16


                                                        <!--replace with hasSpin-->
                                                    </div>

                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w260h196pd8d8d8/6e425e57469d4b41b1b45944903060e2.jpg"/>
                                                    </a>
                                                </figure>
                                            <div class="information-container">
                                                <h2 class="listing-title title-wrap">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click "  href="/classified/advert/201907250430713?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">Porsche Panamera 3.0 TD V6 Tiptronic 5dr</a>
                                                </h2>
                                                <p class="listing-attention-grabber ">*&pound;9,176 Worth of Extras*</p>
                                                <ul class="listing-key-specs ">


                                                                <li>2015 (15 reg)</li>
                                                                
                                                                <li>Hatchback</li>
                                                                
                                                                <li>41,000 miles</li>
                                                                
                                                                <li>3.0L</li>
                                                                
                                                                <li>300bhp</li>
                                                                
                                                                <li>Automatic</li>
                                                                
                                                                <li>Diesel</li>
                                                                

                                                    </ul>
                                                 <ul class="listing-extra-detail">



                                                 </ul>


                                                        <p class="listing-description">FULL PORSCHE SERVICE HISTORY LAST SERVICED AT PORSCHE AT 40,000 Miles.BIG Spec &hellip;</p>
                                                <div class="seller-info seller-profile-link">
                                                    <div class="seller-type  trade-seller">
                                                                    Trade seller - <a href="/dealers/staffordshire/tamworth/rockpoint-bmw-specialists-12069" >See all 30 cars</a>
                                                    </div>


                                                                <div class="seller-location">
                                                <span class="seller-town">tamworth</span> - 
                                                                        101 miles away
                                                                </div>
                                                </div>
                                            </div>
                                                <a class=" js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa href="/classified/advert/201907250430713?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >
                                                    <ul class="listing__thumbnails">
                                                                <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/2e4d2b60fc6f44d385ed0fc95380c284.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/7bf39319222449848fc21d9bed78f189.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/554c8b0b963e4dc295ad49195878401b.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/99a8dfba781443609c7d119439d7d947.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/1d6c63959e97437e93dc552dc66c406c.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/518b9067645f472d8ee66931a3356024.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/57b6ee7f0cc7403bb35d29d5c713bc94.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/796ffd713d794f328db64802e08031ef.jpg" alt=""/>
                                                                </li>
                                                                
                                                    </ul>
                                                </a>
                                        </section>
                                        <section class="price-column  price-with-finance
                                         price-with-pi ">

                                                <a class="js-click-handler listing-fpa-link listings-price-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " href="/classified/advert/201907250430713?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >

                                                        <div data-label="search appearance click" class="vehicle-price">£31,990</div>
                                                </a>

                                                <div class="js-tooltip">
                                                    <span class="search-result__good-great-value pi-indicator js-tooltip-trigger">great Price</span>
                                                    <div class="search-result__valueIndicatorTooltip">
                                                        <div class="tooltip  tooltip__arrow--upRight js-tooltip-window">
                                                            <div class="tooltip-content">
                                                                <h3 class="search-result__valueIndicatorTitle">Why is this car a great price?</h3>
                                                                <span>Auto Trader has price-checked this car against the market value for similar cars and identified it as a great price.</span>
                                                            </div>
                                                            <div class="tooltip-close js-close"></div>
                                                        </div>
                                                    </div>
                                                    <span class="search-result__pi-based-on">Based on similar cars</span>
                                                </div>

                                                        <div class="finance-price-section">
                                                            <a href="/classified/advert/201907250430713?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2"  class="finance-price">
                                                                &pound;580
                                                            </a>
                                                            <p class="finance-label">per month (PCP)</p>

                                                            <div tabindex="0" role="button" aria-label="Open finance example" class="finance-info js-finance-lightbox-trigger tracking-standard-link">Finance example</div>

                                                            <div class="finance-details results-lightbox">

                                                                <div>
                                                                    <span role="button" tabindex="0" aria-label="Close finance example" class="results-lightbox-close js-writeoff-lightbox-close">&#x2715;</span>
                                                                    <h3 class="results-lightbox-title">PCP representative example</h3>
                                                                </div>

                                                                <table class="finance-details__table">
                                                                    <tr>
                                                                        <td>Finance type</td>
                                                                        <td>PCP</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Monthly payments</td>
                                                                        <td>£579.67</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Term</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Contract Length</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>
                                                                                    Cash price
                                                                        </td>
                                                                        <td>£31,990.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Cash deposit</td>
                                                                        <td>£1,000.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount of credit</td>
                                                                        <td>£30,990.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount payable</td>
                                                                        <td>£39,650.41</td>
                                                                    </tr>

                                                                    <tr>
                                                                        <td>Representative APR</td>
                                                                        <td>9.2&#37;</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total charges payable</td>
                                                                        <td>£7,660.41</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Fixed rate of interest pa</td>
                                                                        <td>4.5&#37;</td>
                                                                    </tr>
                                                                        <tr>
                                                                            <td>Optional final payment</td>
                                                                            <td>£11,405.92</td>
                                                                        </tr>
                                                                    <tr>
                                                                        <td>Admin fee</td>
                                                                        <td>£340.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Option to purchase fee</td>
                                                                        <td>£10.00</td>
                                                                    </tr>
                                                                </table>
                                                                <div class="finance-details__product-info">
                                                                    <p class="finance-details__product-info__title">What is PCP?</p>

                                                                                                        <p>Personal contract purchase (PCP) is a flexible way to finance a vehicle. You pay an initial deposit followed by monthly payments (including interest), then at the end of the agreement you have three options:</p>

                                                                                                        <ul class="atc-list">
                                                                                                                                    <li class="atc-list__item">Buy the vehicle by paying the optional final payment (also known as balloon payment) and the optional purchase fee.</li>
                                                                                                                                                            <li class="atc-list__item">Return the vehicle to the dealer and walk away. There may be additional charges if it’s damaged or you’ve exceeded the mileage allowance.</li>
                                                                                                                                                            <li class="atc-list__item">Get a new vehicle on another PCP deal. If the vehicle is worth more than the optional final payment, you can use it as a deposit for your next vehicle.</li>
                                                                                                                                    
                                                                                                        </ul>
                                                                                                    
                                                                                
                                                                    <a href="/car-finance/guides/car-finance-explained" target="_blank" rel="noopener noreferrer">Learn more about finance</a>
                                                                </div>
                                                            </div>
                                                        </div>

                                                            <div class="vehicle-seller-logo  long-logo ">
                                                                <img src="https://dealerlogo.atcdn.co.uk/at2/adbranding/12069/images/searchlogo.gif" alt="Advertiser Logo Rockpoint Bmw Specialists"/>
                                                            </div>


                                                </section>
                                    </article>
                                    <ul class="action-links">
                                        <li>
                                            <a href="https://partnerships-motor-gateway.comparethemarket.com/product/car/start?vrn=AAAABT%2B631gyUQ2t&imageurl=https%3A%2F%2Fm.atcdn.co.uk%2Fa%2Fmedia%2F6e425e57469d4b41b1b45944903060e2.jpg&affclie=DK79&value=31990&numSeats=4&driveSide=Unlisted&advertId=201907250430713" rel="noopener noreferrer nofollow"
                                               class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-insurance-get-quote-initiation" target="_blank">Get an insurance quote</a>
                                        </li>

                                            <li>
                                                <a href="/classified/advert/201907250430713?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2#check-history" rel="noopener noreferrer nofollow"
                                                   class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-vehicle-check-initiation">Check its history</a>
                                            </li>
                                    </ul>
                            </li>




                        



                            <li class="search-page__result"
                                id="201908090958000"

                                data-search-results-advert-card
                                data-advert-id="201908090958000"

                                data-is-group-stock="false"
                                data-is-national-stock-advert="false"
                                data-is-allocated-stock="false"
                                data-is-virtual-stock="false"
                                data-is-network-stock="false"

                                data-image-count="41"
                                data-is-manufacturer-approved="false"
                                data-has-finance="false"
                                data-is-franchise-approved="false"
                                data-good-great-value="low"
                                data-distance-value="159 miles"
                                data-condition-value=""
                            >
                                    <article
                                            data-standout-type=""
                                            class=" search-listing
                                     sso-listing 

                                    ">
                                        <section class="content-column">
                                                <figure class="listing-main-image">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa  href="/classified/advert/201908090958000?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">

                                                    <div class="listing-image-count" data-label="search appearance click ">
                                                        <i data-label="search appearance click " class="listing-image-icon">
                                                            <svg>
                                                                <use xlink:href="/templates/_generated/svg_icons/search-listings.svg#icon-camera"></use>
                                                            </svg>
                                                        </i> 41


                                                        <!--replace with hasSpin-->
                                                    </div>

                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w260h196pd8d8d8/fecd396f833140a7a8ded4b1d139b12f.jpg"/>
                                                    </a>
                                                </figure>
                                            <div class="information-container">
                                                <h2 class="listing-title title-wrap">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click "  href="/classified/advert/201908090958000?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">Porsche Panamera 3.0 [300] V6 Diesel 4dr Tiptronic S Leather Seats</a>
                                                </h2>
                                                <p class="listing-attention-grabber ">Parking cam | SatNav | Cruise</p>
                                                <ul class="listing-key-specs ">


                                                                <li>2015 (15 reg)</li>
                                                                
                                                                <li>Hatchback</li>
                                                                
                                                                <li>38,304 miles</li>
                                                                
                                                                <li>3.0L</li>
                                                                
                                                                <li>300bhp</li>
                                                                
                                                                <li>Automatic</li>
                                                                
                                                                <li>Diesel</li>
                                                                

                                                    </ul>
                                                 <ul class="listing-extra-detail">



                                                 </ul>


                                                        <p class="listing-description">Black - Leather interior with &pound;17495 extras.  Here at CarShop every one of our &hellip;</p>
                                                <div class="seller-info seller-profile-link">
                                                    <div class="seller-type  trade-seller">
                                                                    Trade seller - <a href="/dealers/west-yorkshire/wakefield/carshop-wakefield-8318" >See all 672 cars</a>
                                                    </div>


                                                                <div class="seller-location">
                                                <span class="seller-town">wakefield</span> - 
                                                                        159 miles away
                                                                </div>
                                                </div>
                                            </div>
                                                <a class=" js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa href="/classified/advert/201908090958000?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >
                                                    <ul class="listing__thumbnails">
                                                                <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/1a306a76abae4e5fb18d5d7a50f04e38.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/42096db482a14128bf61d89f1e477106.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/210442f5724147fb9a0b7d45b0ed2d65.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/0ed76e24a14b44c0a92d5d68d4851ca2.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/fedc52793f0e4a819eb8017c2a49adec.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/dea637840c13496a9a35b2b7620ced81.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/92a5bd1027ad4c948c4ba74f95e82fbf.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/4c927c4c2b1a45fea2585b25835036fa.jpg" alt=""/>
                                                                </li>
                                                                
                                                    </ul>
                                                </a>
                                        </section>
                                        <section class="price-column ">

                                                <a class="js-click-handler listing-fpa-link listings-price-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " href="/classified/advert/201908090958000?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >

                                                        <div data-label="search appearance click" class="vehicle-price">£28,999</div>
                                                </a>

                                                <div class="js-tooltip">    <span class="search-result__no-analysis pi-indicator js-tooltip-trigger">Priced Low</span>
                                                    <div class="search-result__valueIndicatorTooltip">
                                                        <div class="tooltip  tooltip__arrow--upRight js-tooltip-window">
                                                            <div class="tooltip-content">
                                                                <h3 class="search-result__valueIndicatorTitle">Why is this car priced low?</h3>
                                                                <span>Auto Trader has price-checked this car against the market value for similar cars and identified it as priced low.</span>
                                                            </div>
                                                            <div class="tooltip-close js-close"></div>
                                                        </div>
                                                    </div>
                                                    <span class="search-result__pi-based-on">Based on similar cars</span></div>

                                                            <div class="vehicle-seller-logo  long-logo ">
                                                                <img src="https://dealerlogo.atcdn.co.uk/at2/adbranding/8318/images/searchlogo.gif" alt="Advertiser Logo CarShop Wakefield"/>
                                                            </div>


                                                </section>
                                    </article>
                                    <ul class="action-links">
                                        <li>
                                            <a href="https://partnerships-motor-gateway.comparethemarket.com/product/car/start?vrn=AAAAB0u7TV2a7KDg&imageurl=https%3A%2F%2Fm.atcdn.co.uk%2Fa%2Fmedia%2Ffecd396f833140a7a8ded4b1d139b12f.jpg&affclie=DK79&value=28999&numSeats=4&driveSide=Unlisted&advertId=201908090958000" rel="noopener noreferrer nofollow"
                                               class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-insurance-get-quote-initiation" target="_blank">Get an insurance quote</a>
                                        </li>

                                            <li>
                                                <a href="/classified/advert/201908090958000?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2#check-history" rel="noopener noreferrer nofollow"
                                                   class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-vehicle-check-initiation">Check its history</a>
                                            </li>
                                    </ul>
                            </li>




                        



                            <li class="search-page__result"
                                id="201906219242547"

                                data-search-results-advert-card
                                data-advert-id="201906219242547"

                                data-is-group-stock="false"
                                data-is-national-stock-advert="false"
                                data-is-allocated-stock="false"
                                data-is-virtual-stock="false"
                                data-is-network-stock="false"

                                data-image-count="38"
                                data-is-manufacturer-approved="false"
                                data-has-finance="true"
                                data-is-franchise-approved="false"
                                data-good-great-value="good"
                                data-distance-value="27 miles"
                                data-condition-value=""
                            >
                                    <article
                                            data-standout-type=""
                                            class=" search-listing
                                     sso-listing 

                                    ">
                                        <section class="content-column">
                                                <figure class="listing-main-image">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa  href="/classified/advert/201906219242547?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">

                                                    <div class="listing-image-count" data-label="search appearance click ">
                                                        <i data-label="search appearance click " class="listing-image-icon">
                                                            <svg>
                                                                <use xlink:href="/templates/_generated/svg_icons/search-listings.svg#icon-camera"></use>
                                                            </svg>
                                                        </i> 38


                                                        <!--replace with hasSpin-->
                                                    </div>

                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w260h196pd8d8d8/7a37d5df43c746739101db8f08b37fe2.jpg"/>
                                                    </a>
                                                </figure>
                                            <div class="information-container">
                                                <h2 class="listing-title title-wrap">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click "  href="/classified/advert/201906219242547?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">Porsche Panamera 3.0 [300] V6 Diesel 4dr Tiptronic S</a>
                                                </h2>
                                                <p class="listing-attention-grabber ">PASM | BOSE | PRIVACY GLASS</p>
                                                <ul class="listing-key-specs ">


                                                                <li>2016 (16 reg)</li>
                                                                
                                                                <li>Hatchback</li>
                                                                
                                                                <li>19,000 miles</li>
                                                                
                                                                <li>3.0L</li>
                                                                
                                                                <li>300bhp</li>
                                                                
                                                                <li>Automatic</li>
                                                                
                                                                <li>Diesel</li>
                                                                

                                                    </ul>
                                                 <ul class="listing-extra-detail">



                                                 </ul>


                                                        <p class="listing-description">Kent Motor Cars are excited to offer this 2016 Porsche Panamera finished in Gloss &hellip;</p>
                                                <div class="seller-info seller-profile-link">
                                                    <div class="seller-type  trade-seller">
                                                                    Trade seller - <a href="/dealers/kent/sevenoaks/kent-motor-cars-10005875" >See all 94 cars</a>
                                                    </div>


                                                                <div class="seller-location">
                                                <span class="seller-town">sevenoaks</span> - 
                                                                        27 miles away
                                                                </div>
                                                </div>
                                            </div>
                                                <a class=" js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa href="/classified/advert/201906219242547?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >
                                                    <ul class="listing__thumbnails">
                                                                <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/e8f56d8efdb443b380b81817a2af0787.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/dc7ac648c98f463e9c9f0942d9525b70.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/7bb11e1927ad45bdbf2525d3f7883db0.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/9ecd909b8cc6444da126fe8fa87e8a2b.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/52ef6a00d8f841f8bf9e76860caba668.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/77087d34b3e24470bace5a217f2eb3db.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/f71654278d7643618db7ad292ef667da.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/a3ec5efdcfe44469b759bba52e94d0a7.jpg" alt=""/>
                                                                </li>
                                                                
                                                    </ul>
                                                </a>
                                        </section>
                                        <section class="price-column  price-with-finance
                                         price-with-pi ">

                                                <a class="js-click-handler listing-fpa-link listings-price-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " href="/classified/advert/201906219242547?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >

                                                        <div data-label="search appearance click" class="vehicle-price">£41,995</div>
                                                </a>

                                                <div class="js-tooltip">
                                                    <span class="search-result__good-great-value pi-indicator js-tooltip-trigger">good Price</span>
                                                    <div class="search-result__valueIndicatorTooltip">
                                                        <div class="tooltip  tooltip__arrow--upRight js-tooltip-window">
                                                            <div class="tooltip-content">
                                                                <h3 class="search-result__valueIndicatorTitle">Why is this car a good price?</h3>
                                                                <span>Auto Trader has price-checked this car against the market value for similar cars and identified it as a good price.</span>
                                                            </div>
                                                            <div class="tooltip-close js-close"></div>
                                                        </div>
                                                    </div>
                                                    <span class="search-result__pi-based-on">Based on similar cars</span>
                                                </div>

                                                        <div class="finance-price-section">
                                                            <a href="/classified/advert/201906219242547?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2"  class="finance-price">
                                                                &pound;1030
                                                            </a>
                                                            <p class="finance-label">per month (HP)</p>

                                                            <div tabindex="0" role="button" aria-label="Open finance example" class="finance-info js-finance-lightbox-trigger tracking-standard-link">Finance example</div>

                                                            <div class="finance-details results-lightbox">

                                                                <div>
                                                                    <span role="button" tabindex="0" aria-label="Close finance example" class="results-lightbox-close js-writeoff-lightbox-close">&#x2715;</span>
                                                                    <h3 class="results-lightbox-title">HP representative example</h3>
                                                                </div>

                                                                <table class="finance-details__table">
                                                                    <tr>
                                                                        <td>Finance type</td>
                                                                        <td>HP</td>
                                                                    </tr>
            

Ran 1 test in 0.758s

OK
                                                        <tr>
                                                                        <td>Monthly payments</td>
                                                                        <td>£1,029.32</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Term</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Contract Length</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>
                                                                                    Cash price
                                                                        </td>
                                                                        <td>£41,995.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Cash deposit</td>
                                                                        <td>£1,000.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount of credit</td>
                                                                        <td>£40,995.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount payable</td>
                                                                        <td>£50,408.36</td>
                                                                    </tr>

                                                                    <tr>
                                                                        <td>Representative APR</td>
                                                                        <td>9.9&#37;</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total charges payable</td>
                                                                        <td>£8,413.36</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Fixed rate of interest pa</td>
                                                                        <td>5.13&#37;</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Option to purchase fee</td>
                                                                        <td>£1.00</td>
                                                                    </tr>
                                                                </table>
                                                                <div class="finance-details__product-info">
                                                                    <p class="finance-details__product-info__title">What is HP?</p>

                                                                                                        <p>Hire purchase (HP) is an affordable way to buy a vehicle as it allows you to pay a deposit, and then make monthly payments to pay off the remaining amount.</p>

                                                                                                                        <p>You’ll be the registered keeper of the vehicle and responsible for insurance, servicing and maintenance, but the finance company will be the legal owner of the vehicle until the outstanding finance (including interest and fees) is paid off.</p>

                                                                                                    
                                                                                
                                                                    <a href="/car-finance/guides/car-finance-explained" target="_blank" rel="noopener noreferrer">Learn more about finance</a>
                                                                </div>
                                                            </div>
                                                        </div>

                                                            <div class="vehicle-seller-logo  long-logo ">
                                                                <img src="https://dealerlogo.atcdn.co.uk/at2/adbranding/10005875/images/searchlogo.gif" alt="Advertiser Logo Kent Motor Cars"/>
                                                            </div>


                                                </section>
                                    </article>
                                    <ul class="action-links">
                                        <li>
                                            <a href="https://partnerships-motor-gateway.comparethemarket.com/product/car/start?vrn=AAAAB1jD%2FJDMwBMN&imageurl=https%3A%2F%2Fm.atcdn.co.uk%2Fa%2Fmedia%2F7a37d5df43c746739101db8f08b37fe2.jpg&affclie=DK79&value=41995&numSeats=4&driveSide=Unlisted&advertId=201906219242547" rel="noopener noreferrer nofollow"
                                               class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-insurance-get-quote-initiation" target="_blank">Get an insurance quote</a>
                                        </li>

                                            <li>
                                                <a href="/classified/advert/201906219242547?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2#check-history" rel="noopener noreferrer nofollow"
                                                   class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-vehicle-check-initiation">Check its history</a>
                                            </li>
                                    </ul>
                            </li>




                        



                            <li class="search-page__result"
                                id="201905117852537"

                                data-search-results-advert-card
                                data-advert-id="201905117852537"

                                data-is-group-stock="false"
                                data-is-national-stock-advert="false"
                                data-is-allocated-stock="false"
                                data-is-virtual-stock="false"
                                data-is-network-stock="false"

                                data-image-count="11"
                                data-is-manufacturer-approved="false"
                                data-has-finance="true"
                                data-is-franchise-approved="false"
                                data-good-great-value="noanalysis"
                                data-distance-value="132 miles"
                                data-condition-value=""
                            >
                                    <article
                                            data-standout-type=""
                                            class=" search-listing
                                     sso-listing 

                                     no-logo ">
                                        <section class="content-column">
                                                <figure class="listing-main-image">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa  href="/classified/advert/201905117852537?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">

                                                    <div class="listing-image-count" data-label="search appearance click ">
                                                        <i data-label="search appearance click " class="listing-image-icon">
                                                            <svg>
                                                                <use xlink:href="/templates/_generated/svg_icons/search-listings.svg#icon-camera"></use>
                                                            </svg>
                                                        </i> 11


                                                        <!--replace with hasSpin-->
                                                    </div>

                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w260h196pd8d8d8/50101a2f54e5494d805894ada9e63314.jpg"/>
                                                    </a>
                                                </figure>
                                            <div class="information-container">
                                                <h2 class="listing-title title-wrap">
                                                    <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click "  href="/classified/advert/201905117852537?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">Porsche Panamera 4.8 V8 4S AWD 5dr</a>
                                                </h2>
                                                <p class="listing-attention-grabber ">Full Porsche Service History</p>
                                                <ul class="listing-key-specs ">


                                                                <li>2010 (10 reg)</li>
                                                                
                                                                <li>Hatchback</li>
                                                                
                                                                <li>50,000 miles</li>
                                                                
                                                                <li>4.8L</li>
                                                                
                                                                <li>400bhp</li>
                                                                
                                                                <li>Automatic</li>
                                                                
                                                                <li>Petrol</li>
                                                                

                                                    </ul>
                                                 <ul class="listing-extra-detail">



                                                 </ul>


                                                        <p class="listing-description">Full Porsche Dealer Service History, recently had new pads and discs on the front &hellip;</p>
                                                <div class="seller-info ">
                                                    <div class="seller-type ">
                                                                    Private seller
                                                    </div>


                                                                <div class="seller-location">
                                                <span class="seller-town">worksop</span> - 
                                                                        132 miles away
                                                                </div>
                                                </div>
                                            </div>
                                                <a class=" js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa href="/classified/advert/201905117852537?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >
                                                    <ul class="listing__thumbnails">
                                                                <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/75cb88cbb2994239a51be93a312dbbf8.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/f0066cd8a20b4811868ea2701d21f18c.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/9bae1ed2137c4eb5a0ed5ee376d093d8.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/06ec35978da349268eedc03b8cbf7e56.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/f7421e62b6214df496b2c9225f5d0174.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/fa75ac2e14e943349b3c726e8529a3fd.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/808505f1aed54508b27fe3a6266d7b00.jpg" alt=""/>
                                                                </li>
                                                                        <li>
                                                                    <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/c00fa1f2b96d450692933500ac6274bc.jpg" alt=""/>
                                                                </li>
                                                                
                                                    </ul>
                                                </a>
                                        </section>
                                        <section class="price-column  price-with-finance
                                        ">

                                                <a class="js-click-handler listing-fpa-link listings-price-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " href="/classified/advert/201905117852537?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" >

                                                        <div data-label="search appearance click" class="vehicle-price">£22,000</div>
                                                </a>


                                                        <div class="finance-price-section">
                                                            <a href="/classified/advert/201905117852537?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2"  class="finance-price">
                                                                &pound;621
                                                            </a>
                                                            <p class="finance-label">per month (HP)</p>

                                                            <div tabindex="0" role="button" aria-label="Open finance example" class="finance-info js-finance-lightbox-trigger tracking-standard-link">Finance example</div>

                                                            <div class="finance-details results-lightbox">

                                                                <div>
                                                                    <span role="button" tabindex="0" aria-label="Close finance example" class="results-lightbox-close js-writeoff-lightbox-close">&#x2715;</span>
                                                                    <h3 class="results-lightbox-title">HP representative example</h3>
                                                                </div>

                                                                <table class="finance-details__table">
                                                                    <tr>
                                                                        <td>Finance type</td>
                                                                        <td>HP</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Monthly payments</td>
                                                                        <td>£620.03</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Term</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Contract Length</td>
                                                                        <td>48 months</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>
                                                                                    Cash price
                                                                        </td>
                                                                        <td>£22,000.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Cash deposit</td>
                                                                        <td>£1,000.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount of credit</td>
                                                                        <td>£21,000.00</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total amount payable</td>
                                                                        <td>£30,762.44</td>
                                                                    </tr>

                                                                    <tr>
                                                                        <td>Representative APR</td>
                                                                        <td>19.9&#37;</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Total charges payable</td>
                                                                        <td>£8,762.44</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Fixed rate of interest pa</td>
                                                                        <td>10.43&#37;</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td>Option to purchase fee</td>
                                                                        <td>£1.00</td>
                                                                    </tr>
                                                                </table>
                                                                <div class="finance-details__product-info">
                                                                    <p class="finance-details__product-info__title">What is HP?</p>

                                                                                                        <p>Hire purchase (HP) is an affordable way to buy a vehicle as it allows you to pay a deposit, and then make monthly payments to pay off the remaining amount.</p>

                                                                                                                        <p>You’ll be the registered keeper of the vehicle and responsible for insurance, servicing and maintenance, but the finance company will be the legal owner of the vehicle until the outstanding finance (including interest and fees) is paid off.</p>

                                                                                                    
                                                                                
                                                                    <a href="/car-finance/guides/car-finance-explained" target="_blank" rel="noopener noreferrer">Learn more about finance</a>
                                                                </div>
                                                            </div>
                                                        </div>


                                                </section>
                                    </article>
                                    <ul class="action-links">
                                        <li>
                                            <a href="https://partnerships-motor-gateway.comparethemarket.com/product/car/start?vrn=AAAAB0e1HE3g55qD&imageurl=https%3A%2F%2Fm.atcdn.co.uk%2Fa%2Fmedia%2F50101a2f54e5494d805894ada9e63314.jpg&affclie=DK78&value=22000&numSeats=4&driveSide=Unlisted&advertId=201905117852537" rel="noopener noreferrer nofollow"
                                               class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-insurance-get-quote-initiation" target="_blank">Get an insurance quote</a>
                                        </li>

                                            <li>
                                                <a href="/classified/advert/201905117852537?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2#check-history" rel="noopener noreferrer nofollow"
                                                   class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-vehicle-check-initiation">Check its history</a>
                                            </li>
                                    </ul>
                            </li>



                                                                        <li class="search-page__result"
                                                                            id="201909252617566"

                                                                            data-search-results-advert-card
                                                                            data-advert-id="201909252617566"

                                                                            data-is-promoted-listing="true"

                                                                            data-image-count="42"
                                                                            data-is-manufacturer-approved="false"
                                                                            data-has-finance="true"
                                                                            data-is-franchise-approved="false"
                                                                            data-good-great-value="high"
                                                                            data-distance-value="133 miles"
                                                                            data-condition-value=""
                                                                        >
                                                                                <span class="listings-standout">Promoted listing</span><article
                                                                                        data-standout-type="promoted"
                                                                                        class="js-standout-listing  search-listing
                                                                                 sso-listing 

                                                                                ">
                                                                                    <section class="content-column">
                                                                                            <figure class="listing-main-image">
                                                                                                <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa rel="nofollow" href="/classified/advert/201909252617566?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">

                                                                                                <div class="listing-image-count" data-label="search appearance click ">
                                                                                                    <i data-label="search appearance click " class="listing-image-icon">
                                                                                                        <svg>
                                                                                                            <use xlink:href="/templates/_generated/svg_icons/search-listings.svg#icon-camera"></use>
                                                                                                        </svg>
                                                                                                    </i> 42


                                                                                                    <!--replace with hasSpin-->
                                                                                                </div>

                                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w260h196pd8d8d8/78e9147638924500a24284e77f821261.jpg"/>
                                                                                                </a>
                                                                                            </figure>
                                                                                        <div class="information-container">
                                                                                            <h2 class="listing-title title-wrap">
                                                                                                <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " rel="nofollow" href="/classified/advert/201909252617566?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">Porsche Panamera 3.0 D V6 TIPTRONIC 5d AUTO 300 BHP FULL &hellip;</a>
                                                                                            </h2>
                                                                                            <p class="listing-attention-grabber ">SAT NAV-BLUETOOTH-DAB-MEDIA-</p>
                                                                                            <ul class="listing-key-specs ">


                                                                                                            <li>2014 (64 reg)</li>
                                                                                                            
                                                                                                            <li>Hatchback</li>
                                                                                                            
                                                                                                            <li>58,091 miles</li>
                                                                                                            
                                                                                                            <li>3.0L</li>
                                                                                                            
                                                                                                            <li>300bhp</li>
                                                                                                            
                                                                                                            <li>Automatic</li>
                                                                                                            
                                                                                                            <li>Diesel</li>
                                                                                                            

                                                                                                </ul>
                                                                                             <ul class="listing-extra-detail">



                                                                                             </ul>


                                                                                                    <p class="listing-description">Ambient temperature display Brake pad wear sensors Instrument cluster with &hellip;</p>
                                                                                            <div class="seller-info seller-profile-link">
                                                                                                <div class="seller-type  trade-seller">
                                                                                                                Trade seller - <a href="/dealers/city-of-cardiff/cardiff/cardiff-trade-sales-50169" rel="nofollow">See all 68 cars</a>
                                                                                                </div>


                                                                                                            <div class="seller-location">
                                                                                            <span class="seller-town">cardiff</span> - 
                                                                                                                    133 miles away
                                                                                                            </div>
                                                                                            </div>
                                                                                        </div>
                                                                                            <a class=" js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa href="/classified/advert/201909252617566?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" rel="nofollow">
                                                                                                <ul class="listing__thumbnails">
                                                                                                            <li>
                                                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/edee0593c58a439bbeb4fe4431409130.jpg" alt=""/>
                                                                                                            </li>
                                                                                                                    <li>
                                                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/4c661c121a4f44c1a646f1c2f102b055.jpg" alt=""/>
                                                                                                            </li>
                                                                                                                    <li>
                                                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/4a18a267a3f44f569990548b94801a2a.jpg" alt=""/>
                                                                                                            </li>
                                                                                                                    <li>
                                                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/d9176e33a52e4e0689fc0327bb6b6c25.jpg" alt=""/>
                                                                                                            </li>
                                                                                                                    <li>
                                                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/4dcabe4a4bd143afa9a695d8212e9e9e.jpg" alt=""/>
                                                                                                            </li>
                                                                                                                    <li>
                                                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/c8fa6b17d6c344408eacb702c9ddd2b5.jpg" alt=""/>
                                                                                                            </li>
                                                                                                                    <li>
                                                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/cf2097a59a1c4492bf09beb4598d41d0.jpg" alt=""/>
                                                                                                            </li>
                                                                                                                    <li>
                                                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/39b8e37bc3d74ba58275c85a773b8164.jpg" alt=""/>
                                                                                                            </li>
                                                                                                            
                                                                                                </ul>
                                                                                            </a>
                                                                                    </section>
                                                                                    <section class="price-column  price-with-finance
                                                                                    ">

                                                                                            <a class="js-click-handler listing-fpa-link listings-price-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " href="/classified/advert/201909252617566?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" rel="nofollow">

                                                                                                    <div data-label="search appearance click" class="vehicle-price">£31,991</div>
                                                                                            </a>


                                                                                                    <div class="finance-price-section">
                                                                                                        <a href="/classified/advert/201909252617566?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" rel="nofollow" class="finance-price">
                                                                                                            &pound;620
                                                                                                        </a>
                                                                                                        <p class="finance-label">per month (PCP)</p>

                                                                                                        <div tabindex="0" role="button" aria-label="Open finance example" class="finance-info js-finance-lightbox-trigger tracking-standard-link">Finance example</div>

                                                                                                        <div class="finance-details results-lightbox">

                                                                                                            <div>
                                                                                                                <span role="button" tabindex="0" aria-label="Close finance example" class="results-lightbox-close js-writeoff-lightbox-close">&#x2715;</span>
                                                                                                                <h3 class="results-lightbox-title">PCP representative example</h3>
                                                                                                            </div>

                                                                                                            <table class="finance-details__table">
                                                                                                                <tr>
                                                                                                                    <td>Finance type</td>
                                                                                                                    <td>PCP</td>
                                                                                                                </tr>
                                                                                                                <tr>
                                                                                                                    <td>Monthly payments</td>
                                                                                                                    <td>£619.21</td>
                                                                                                                </tr>
                                                                                                                <tr>
                                                                                                                    <td>Term</td>
                                                                                                                    <td>48 months</td>
                                                                                                                </tr>
                                                                                                                <tr>
                                                                                                                    <td>Contract Length</td>
                                                                                                                    <td>48 months</td>
                                                                                                                </tr>
                                                                                                                <tr>
                                                                                                                    <td>
                                                                                                                                Cash price
                                                                                                                    </td>
                                                                                                                    <td>£31,991.00</td>
                                                                                                                </tr>
                                                                                                                <tr>
                                                                                                                    <td>Cash deposit</td>
                                                                                                                    <td>£1,000.00</td>
                                                                                                                </tr>
                                                                                                                <tr>
                                                                                                                    <td>Total amount of credit</td>
                                                                                                                    <td>£30,991.00</td>
                                                                                                                </tr>
                                                                                                                <tr>
                                                                                                                    <td>Total amount payable</td>
                                                                                                                    <td>£39,960.87</td>
                                                                                                                </tr>

                                                                                                                <tr>
                                                                                                                    <td>Representative APR</td>
                                                                                                                    <td>9.9&#37;</td>
                                                                                                                </tr>
                                                                                                                <tr>
                                                                                                                    <td>Total charges payable</td>
                                                                                                                    <td>£7,969.87</td>
                                                                                                                </tr>
                                                                                                                <tr>
                                                                                                                    <td>Fixed rate of interest pa</td>
                                                                                                                    <td>9.9&#37;</td>
                                                                                                                </tr>
                                                                                                                    <tr>
                                                                                                                        <td>Optional final payment</td>
                                                                                                                        <td>£9,858.00</td>
                                                                                                                    </tr>
                                                                                                            </table>
                                                                                                            <div class="finance-details__product-info">
                                                                                                                <p class="finance-details__product-info__title">What is PCP?</p>

                                                                                                                                                    <p>Personal contract purchase (PCP) is a flexible way to finance a vehicle. You pay an initial deposit followed by monthly payments (including interest), then at the end of the agreement you have three options:</p>

                                                                                                                                                    <ul class="atc-list">
                                                                                                                                                                                <li class="atc-list__item">Buy the vehicle by paying the optional final payment (also known as balloon payment) and the optional purchase fee.</li>
                                                                                                                                                                                                        <li class="atc-list__item">Return the vehicle to the dealer and walk away. There may be additional charges if it’s damaged or you’ve exceeded the mileage allowance.</li>
                                                                                                                                                                                                        <li class="atc-list__item">Get a new vehicle on another PCP deal. If the vehicle is worth more than the optional final payment, you can use it as a deposit for your next vehicle.</li>
                                                                                                                                                                                
                                                                                                                                                    </ul>
                                                                                                                                                
                                                                                                                            
                                                                                                                <a href="/car-finance/guides/car-finance-explained" target="_blank" rel="noopener noreferrer">Learn more about finance</a>
                                                                                                            </div>
                                                                                                        </div>
                                                                                                    </div>

                                                                                                        <div class="vehicle-seller-logo  long-logo ">
                                                                                                            <img src="https://dealerlogo.atcdn.co.uk/at2/adbranding/50169/images/searchlogo.gif" alt="Advertiser Logo Cardiff Trade Sales"/>
                                                                                                        </div>


                                                                                            </section>
                                                                                </article>
                                                                                <ul class="action-links">
                                                                                    <li>
                                                                                        <a href="https://partnerships-motor-gateway.comparethemarket.com/product/car/start?vrn=AAAAB9f1N78qKQj9&imageurl=https%3A%2F%2Fm.atcdn.co.uk%2Fa%2Fmedia%2F78e9147638924500a24284e77f821261.jpg&affclie=DK79&value=31991&numSeats=4&driveSide=Unlisted&advertId=201909252617566" rel="noopener noreferrer nofollow"
                                                                                           class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-insurance-get-quote-initiation" target="_blank">Get an insurance quote</a>
                                                                                    </li>

                                                                                        <li>
                                                                                            <a href="/classified/advert/201909252617566?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2#check-history" rel="noopener noreferrer nofollow"
                                                                                               class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-vehicle-check-initiation">Check its history</a>
                                                                                        </li>
                                                                                </ul>
                                                                        </li>
                                                                    

                                        <li class="search-page__result"
                                            id="201909252598088"

                                            data-search-results-advert-card
                                            data-advert-id="201909252598088"

                                            data-is-ymal-listing="true"

                                            data-image-count="30"
                                            data-is-manufacturer-approved="true"
                                            data-has-finance="true"
                                            data-is-franchise-approved="false"
                                            data-good-great-value="high"
                                            data-distance-value="363 miles"
                                            data-condition-value=""
                                         >
                                                <span class="listings-standout">You may also like</span><article
                                                        data-standout-type="ymal"
                                                        class="js-standout-listing  search-listing
                                                 sso-listing 

                                                ">
                                                    <section class="content-column">
                                                            <figure class="listing-main-image">
                                                                <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa rel="nofollow" href="/classified/advert/201909252598088?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">

                                                                <div class="listing-image-count" data-label="search appearance click ">
                                                                    <i data-label="search appearance click " class="listing-image-icon">
                                                                        <svg>
                                                                            <use xlink:href="/templates/_generated/svg_icons/search-listings.svg#icon-camera"></use>
                                                                        </svg>
                                                                    </i> 30


                                                                    <!--replace with hasSpin-->
                                                                </div>

                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w260h196pd8d8d8/b9ba0685b6bc4003935d79664e703837.jpg"/>
                                                                </a>
                                                            </figure>
                                                        <div class="information-container">
                                                            <h2 class="listing-title title-wrap">
                                                                <a class="js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " rel="nofollow" href="/classified/advert/201909252598088?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2">Porsche Panamera Diesel Saloon 3.0 [300] V6 Diesel 4dr Tiptronic S</a>
                                                            </h2>
                                                            <p class="listing-attention-grabber ">AirSuspension/Sunroof/BOSE</p>
                                                            <ul class="listing-key-specs ">


                                                                            <li>2015 (15 reg)</li>
                                                                            
                                                                            <li>Hatchback</li>
                                                                            
                                                                            <li>37,847 miles</li>
                                                                            
                                                                            <li>3.0L</li>
                                                                            
                                                                            <li>300bhp</li>
                                                                            
                                                                            <li>Automatic</li>
                                                                            
                                                                            <li>Diesel</li>
                                                                            

                                                                </ul>
                                                             <ul class="listing-extra-detail">
                                                                        <li>Manufacturer Approved</li>



                                                             </ul>


                                                                    <p class="listing-description">An incredible opportunity to combine comfort, elegance and economy behind the &hellip;</p>
                                                            <div class="seller-info seller-profile-link">
                                                                <div class="seller-type  trade-seller">
                                                                                Trade seller - <a href="/dealers/porsche-centre-perth-10013602" rel="nofollow">See all 31 cars</a>
                                                                </div>


                                                                            <div class="seller-location">
                                                                                    363 miles away
                                                                            </div>
                                                            </div>
                                                        </div>
                                                            <a class=" js-click-handler listing-fpa-link tracking-standard-link" data-results-nav-fpa href="/classified/advert/201909252598088?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" rel="nofollow">
                                                                <ul class="listing__thumbnails">
                                                                            <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/b8fdb371c10143aeb887bab4ad2396db.jpg" alt=""/>
                                                                            </li>
                                                                                    <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/e1d9d285487d4f389cac614e28e03997.jpg" alt=""/>
                                                                            </li>
                                                                                    <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/6a70dc4c117d4a4193e3a418d04c3f53.jpg" alt=""/>
                                                                            </li>
                                                                                    <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/a524c8db16fc4518aa6f57d609f1fc00.jpg" alt=""/>
                                                                            </li>
                                                                                    <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/5dac75fbc17d4d65b4bbb937173f8032.jpg" alt=""/>
                                                                            </li>
                                                                                    <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/5532a596ce3b47879a5cade15258e3db.jpg" alt=""/>
                                                                            </li>
                                                                                    <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/7a357e510fd54b92ace432a86f775b58.jpg" alt=""/>
                                                                            </li>
                                                                                    <li>
                                                                                <img data-label="search appearance click " src="https://m.atcdn.co.uk/a/media/w81h61pdfdfdf/4dbec4e0d7474e4aa55e19b5d35085ea.jpg" alt=""/>
                                                                            </li>
                                                                            
                                                                </ul>
                                                            </a>
                                                    </section>
                                                    <section class="price-column  price-with-finance
                                                    ">

                                                            <a class="js-click-handler listing-fpa-link listings-price-link tracking-standard-link" data-results-nav-fpa data-label="search appearance click " href="/classified/advert/201909252598088?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" rel="nofollow">

                                                                    <div data-label="search appearance click" class="vehicle-price">£39,900</div>
                                                            </a>


                                                                    <div class="finance-price-section">
                                                                        <a href="/classified/advert/201909252598088?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2" rel="nofollow" class="finance-price">
                                                                            &pound;727
                                                                        </a>
                                                                        <p class="finance-label">per month (PCP)</p>

                                                                        <div tabindex="0" role="button" aria-label="Open finance example" class="finance-info js-finance-lightbox-trigger tracking-standard-link">Finance example</div>

                                                                        <div class="finance-details results-lightbox">

                                                                            <div>
                                                                                <span role="button" tabindex="0" aria-label="Close finance example" class="results-lightbox-close js-writeoff-lightbox-close">&#x2715;</span>
                                                                                <h3 class="results-lightbox-title">PCP representative example</h3>
                                                                            </div>

                                                                            <table class="finance-details__table">
                                                                                <tr>
                                                                                    <td>Finance type</td>
                                                                                    <td>PCP</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Monthly payments</td>
                                                                                    <td>£726.63</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Term</td>
                                                                                    <td>48 months</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Contract Length</td>
                                                                                    <td>48 months</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>
                                                                                                Cash price
                                                                                    </td>
                                                                                    <td>£39,900.00</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Cash deposit</td>
                                                                                    <td>£1,000.00</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Total amount of credit</td>
                                                                                    <td>£38,900.00</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Total amount payable</td>
                                                                                    <td>£46,804.57</td>
                                                                                </tr>

                                                                                <tr>
                                                                                    <td>Representative APR</td>
                                                                                    <td>6.9&#37;</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Total charges payable</td>
                                                                                    <td>£6,904.57</td>
                                                                                </tr>
                                                                                <tr>
                                                                                    <td>Fixed rate of interest pa</td>
                                                                                    <td>6.89&#37;</td>
                                                                                </tr>
                                                                                    <tr>
                                                                                        <td>Optional final payment</td>
                                                                                        <td>£11,652.96</td>
                                                                                    </tr>
                                                                            </table>
                                                                            <div class="finance-details__product-info">
                                                                                <p class="finance-details__product-info__title">What is PCP?</p>

                                                                                                                    <p>Personal contract purchase (PCP) is a flexible way to finance a vehicle. You pay an initial deposit followed by monthly payments (including interest), then at the end of the agreement you have three options:</p>

                                                                                                                    <ul class="atc-list">
                                                                                                                                                <li class="atc-list__item">Buy the vehicle by paying the optional final payment (also known as balloon payment) and the optional purchase fee.</li>
                                                                                                                                                                        <li class="atc-list__item">Return the vehicle to the dealer and walk away. There may be additional charges if it’s damaged or you’ve exceeded the mileage allowance.</li>
                                                                                                                                                                        <li class="atc-list__item">Get a new vehicle on another PCP deal. If the vehicle is worth more than the optional final payment, you can use it as a deposit for your next vehicle.</li>
                                                                                                                                                
                                                                                                                    </ul>
                                                                                                                
                                                                                            
                                                                                <a href="/car-finance/guides/car-finance-explained" target="_blank" rel="noopener noreferrer">Learn more about finance</a>
                                                                            </div>
                                                                        </div>
                                                                    </div>

                                                                        <div class="vehicle-seller-logo  long-logo ">
                                                                                    <span class="listing-approved-logo"><img src="/images/approved/search/porsche.gif" alt="Advertiser Logo Porsche Centre Perth"/></span>
                                                                            <img src="https://dealerlogo.atcdn.co.uk/at2/adbranding/10013602/images/searchlogo.gif" alt="Advertiser Logo Porsche Centre Perth"/>
                                                                        </div>


                                                            </section>
                                                </article>
                                                <ul class="action-links">
                                                    <li>
                                                        <a href="https://partnerships-motor-gateway.comparethemarket.com/product/car/start?vrn=AAAABy43hvA2GgEz&imageurl=https%3A%2F%2Fm.atcdn.co.uk%2Fa%2Fmedia%2Fb9ba0685b6bc4003935d79664e703837.jpg&affclie=DK79&value=39900&numSeats=4&driveSide=Unlisted&advertId=201909252598088" rel="noopener noreferrer nofollow"
                                                           class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-insurance-get-quote-initiation" target="_blank">Get an insurance quote</a>
                                                    </li>

                                                        <li>
                                                            <a href="/classified/advert/201909252598088?make=PORSCHE&advertising-location=at_cars&model=PANAMERA&radius=1500&sort=sponsored&postcode=n1c4ag&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&page=2#check-history" rel="noopener noreferrer nofollow"
                                                               class="tracking-motoring-products-link action-anchor" data-label="fpa-tile-vehicle-check-initiation">Check its history</a>
                                                        </li>
                                                </ul>
                                        </li>



                        


        </ul>

            <nav class="pagination">
                <ul class="pagination--ul">

                        <li class="pagination--li">
                            <a class="pagination--left__active" href="https://www.autotrader.co.uk/results-car-search/page/1" rel="nofollow" data-paginate="1" data-to-top="true">
                                <i class="icon">
                                    <svg><use xlink:href="/templates/_generated/svg_icons/common.svg#icon-arrow-left"></use></svg>
                                </i>
                                <span class="pagination__text">Previous</span>
                            </a>
                        </li>



                                <li class="pagination--li">
                                    <a href="https://www.autotrader.co.uk/results-car-search/page/1" rel="nofollow" data-paginate="1" data-to-top="true">1</a>
                                </li>
                            

                    <li class="pagination--li">
                        2
                    </li>


                                <li class="pagination--li">
                                    <a href="https://www.autotrader.co.uk/results-car-search/page/3" rel="nofollow" data-paginate="3" data-to-top="true">3</a>
                                </li>
                            
                                <li class="pagination--li">
                                    <a href="https://www.autotrader.co.uk/results-car-search/page/4" rel="nofollow" data-paginate="4" data-to-top="true">4</a>
                                </li>
                            
                                <li class="pagination--li">
                                    <a href="https://www.autotrader.co.uk/results-car-search/page/5" rel="nofollow" data-paginate="5" data-to-top="true">5</a>
                                </li>
                            
                                <li class="pagination--li">
                                    <a href="https://www.autotrader.co.uk/results-car-search/page/6" rel="nofollow" data-paginate="6" data-to-top="true">6</a>
                                </li>
                            

                        <li class="pagination--li">
                            <a class="pagination--right__active" href="https://www.autotrader.co.uk/results-car-search/page/3" rel="nofollow" data-paginate="3" data-to-top="true">
                            <i class="icon">
                                <svg><use xlink:href="/templates/_generated/svg_icons/common.svg#icon-arrow-right"></use></svg>
                            </i>
                                <span class="pagination__text">Next</span>
                            </a>
                        </li>
                </ul>
            </nav>
    <div class="search-results__overlay">
        <div class="search-results__overlay-spinner">
            <svg class="loading-spinner__icon"><title>Loading Spinner Icon</title><use xlink:href="/templates/_generated/svg_icons/common.svg#icon-loading-spinner" /></svg>
            <br/>Loading...
        </div>
    </div>
    <div id="js-search-result-adsense-slot" data-replace-ad-sense=true>
    </div>

    <script type="text/javascript">
        new_utag_data = {"platform":"desktop","make":"porsche","model":"panamera","page_name":"cars:search:known:results","page_name_granular":"desktop:cars:search:known:results-pg[2]","channel":"cars","section":"search","location_postcode":"n1c4ag","location_key":"4860bf8eaaca2cc7","location_lat_long":"51.5329411752,-0.1250358958","vehicles_found":"411","distance":"1500","search_criteria":"make,model,distance","used_new":"used,nearlynew,new","sort_order":"sponsored","page_number":"2","location_area":"londonnorthlower","loc_one":"n1c4","location_postcode_prefix":"n1c","environment":"www","experiment_variant":"cape-rxC-dmI-rrT-dnT-dpI-d0C-dg2-drI-dvT-csI-zpI-lfT-l4C-nvC-sbI-dtI","aoi":"PEU159,HYU050,FIA001,MIN099,BMW006,FER007,VWA001","userid":"ID\u003d2aed52bc-3b91-4b4b-b202-b5805da4c481"}
    </script>

</div>'''
