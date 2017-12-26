TOURKENYA

Software track:
This project was implemented usong the cs50 ide, sql database, javascript, python's flask as well as HTML template.

For the aesthetics of the project, we adopted a html layout from Euro-Travel masters which we used as a base for our templates.
We modified the template to suit every page that we needed, and we added some javascript features such as an overlay that showed the progress of the loading page.

The very first page that the user sees in this website is the home page which displays pictures of some tourist attractions in the
Kenya, accompanied by a carousel that shows 10 national parks all with links to their decriptions. We also implemented a carousel
of the hotels near the tour sites together with links to their descriptions. We manually added data for the hotels and tourism
sites into our database since we couldn't find an API that contains the hotels and attractions specific to Kenya. We linked the
hotels and the attraction sites via the name of the attraction site.

The descriptions of the attraction sites, that can be accesses by clicking a button hovering over the picture of the attraction site
in the carousel contains pictures of the attraction site that whose google links we stored in our database. In addition, we used a
wikipedia API to generate a short summary of the attraction site. We also include as part of the description a 4K video whose youtube
links we stored in the database next to each respective attraction site.

We generated tourism packages since it is convenient for the user of the website to book an all-in-one package instead of figuring
out each single detail of the trip. Each package includes one hotel, one tour-agency and a certain tourist attraction, with meals, transport
and accommodation all included in the cost.
each package has a price that is a sum of all the relevant costs per day, including our booking fee (We take out a small fee from every package as our source of revenue).
We generated the packages dynamically using an algorithm that matched up all hotels and companys that operate in the same area. The algorithm
which iterated over the resorts of a certain attraction site and matched it with each tour company and added all the relevant fields
into a packages table in the databas. Since we wanted only a very basic implementation for this project, we only included 3 tour-agencies
which had access to all the tourist attractions and hotels.

The description page has three random packages selected from the many packages in the database that are place specific. This means that,
in the description the user will only view the packages that are related to the place he wishes to go to. At the bottom of each package
is a small form which asks the user to inout the start and end date of the safari together with the number of people he/she wishes to
bring along. The user then adds the package to cart( which we input into the database on the back end) and immediately and alert is
raised that item has been added to cart, without redirecting the user.

The user can further view cart, remove items from the cart or checkout a particular package which will redirect him to a form that asks
for his billing information which on submission generate a receipt.