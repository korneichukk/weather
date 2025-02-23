import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

import pandas as pd
from pathlib import Path

from src.database.db import AsyncSessionLocal
from src.database.models import City
from src.config import get_settings

settings = get_settings()


continent_country_map = {
    "Asia": [
        "Japan",
        "Indonesia",
        "India",
        "China",
        "Philippines",
        "Korea, South",
        "Bangladesh",
        "Thailand",
        "Russia",
        "Pakistan",
        "Vietnam",
        "Iran",
        "Iraq",
        "Saudi Arabia",
        "Singapore",
        "Malaysia",
        "South Korea",
        "Afghanistan",
        "Turkey",
        "Israel",
        "Sri Lanka",
        "Jordan",
        "Azerbaijan",
        "Kuwait",
        "Kazakhstan",
        "Nepal",
        "Armenia",
        "Oman",
        "Georgia",
        "Cyprus",
        "Tajikistan",
        "Mongolia",
        "Yemen",
        "Kuwait",
        "Lebanon",
        "Syria",
        "Hong Kong",
        "Macau",
        "Taiwan",
        "Korea, North",
    ],
    "Africa": [
        "Egypt",
        "Nigeria",
        "South Africa",
        "Kenya",
        "Angola",
        "Ethiopia",
        "Morocco",
        "Algeria",
        "Ghana",
        "Uganda",
        "Tanzania",
        "Sudan",
        "Zimbabwe",
        "Malawi",
        "Mozambique",
        "Namibia",
        "Zambia",
        "Ivory Coast",
        "Senegal",
        "Cameroon",
        "Mauritius",
        "Mali",
        "Madagascar",
        "Botswana",
        "Mauritania",
        "Tunisia",
        "Burkina Faso",
        "Rwanda",
        "Chad",
        "Gabon",
        "Liberia",
        "Sierra Leone",
        "Lesotho",
        "Eswatini",
        "Seychelles",
        "Burundi",
        "Ghana",
        "Togo",
        "Sao Tome and Principe",
        "Comoros",
        "Central African Republic",
        "Congo (Kinshasa)",
        "Congo (Brazzaville)",
        "Equatorial Guinea",
        "Gabon",
        "Gambia",
        "Guinea",
        "Guinea-Bissau",
        "Congo",
    ],
    "North America": [
        "United States",
        "Mexico",
        "Canada",
        "Guatemala",
        "Honduras",
        "El Salvador",
        "Costa Rica",
        "Panama",
        "Cuba",
        "Dominican Republic",
        "Haiti",
        "Jamaica",
        "Trinidad and Tobago",
        "Barbados",
        "Saint Lucia",
        "Saint Kitts and Nevis",
        "Antigua and Barbuda",
        "Bahamas",
        "Belize",
        "Saint Vincent and the Grenadines",
        "Bermuda",
        "Cayman Islands",
        "Puerto Rico",
        "Dominica",
        "Grenada",
        "Saint Barthelemy",
        "Saint Martin",
        "Faroe Islands",
    ],
    "South America": [
        "Brazil",
        "Argentina",
        "Peru",
        "Colombia",
        "Chile",
        "Ecuador",
        "Bolivia",
        "Paraguay",
        "Suriname",
        "Guyana",
        "Venezuela",
        "Uruguay",
        "French Guiana",
    ],
    "Europe": [
        "United Kingdom",
        "France",
        "Germany",
        "Italy",
        "Spain",
        "Poland",
        "Ukraine",
        "Romania",
        "Netherlands",
        "Belgium",
        "Greece",
        "Portugal",
        "Czechia",
        "Sweden",
        "Hungary",
        "Belarus",
        "Austria",
        "Switzerland",
        "Norway",
        "Denmark",
        "Finland",
        "Ireland",
        "Croatia",
        "Serbia",
        "Bulgaria",
        "Slovakia",
        "Slovenia",
        "Moldova",
        "Albania",
        "Kosovo",
        "North Macedonia",
        "Georgia",
        "Lithuania",
        "Latvia",
        "Estonia",
        "Armenia",
        "Malta",
        "San Marino",
        "Monaco",
        "Liechtenstein",
        "Andorra",
        "Cyprus",
        "Luxembourg",
        "Malta",
        "Vatican City",
        "Faroe Islands",
    ],
    "Oceania": [
        "Australia",
        "New Zealand",
        "Fiji",
        "Papua New Guinea",
        "Solomon Islands",
        "Vanuatu",
        "Samoa",
        "Kiribati",
        "Tonga",
        "Tuvalu",
        "Palau",
        "Micronesia",
        "Marshall Islands",
        "Nauru",
        "Cook Islands",
        "French Polynesia",
        "New Caledonia",
        "Wallis and Futuna",
        "American Samoa",
        "Cabo Verde",
        "Guam",
    ],
    "Antarctica": ["Antarctica"],
    "Other": [
        "Burma",
        "Côte d’Ivoire",
        "United Arab Emirates",
        "Uzbekistan",
        "Somalia",
        "Cambodia",
        "Qatar",
        "Libya",
        "Kyrgyzstan",
        "Nicaragua",
        "Turkmenistan",
        "Niger",
        "Eritrea",
        "Laos",
        "Benin",
        "Bahrain",
        "Djibouti",
        "Gaza Strip",
        "Macau",
        "South Sudan",
        "Bosnia and Herzegovina",
        "Gambia, The",
        "Reunion",
        "Bahamas, The",
        "Martinique",
        "Guadeloupe",
        "Timor-Leste",
        "West Bank",
        "Montenegro",
        "Curaçao",
        "Iceland",
        "Maldives",
        "Bhutan",
        "Mayotte",
        "Brunei",
        "Aruba",
        "Gibraltar",
        "Jersey",
        "Isle of Man",
        "Guernsey",
        "Greenland",
        "Micronesia, Federated States of",
        "Virgin Islands, British",
        "Bonaire, Sint Eustatius, and Saba",
        "Saint Pierre and Miquelon",
        "Turks and Caicos Islands",
        "Anguilla",
        "Northern Mariana Islands",
        "Falkland Islands (Islas Malvinas)",
        "Sint Maarten",
        "Svalbard",
        "Christmas Island",
        "Saint Helena, Ascension, and Tristan da Cunha",
        "Niue",
        "Montserrat",
        "Norfolk Island",
        "South Georgia and South Sandwich Islands",
        "Pitcairn Islands",
        "South Georgia And South Sandwich Islands",
        "U.S. Virgin Islands",
    ],
}


async def populate_cities_from_csv(csv_file_path: Path, session: AsyncSession) -> None:
    df = pd.read_csv(csv_file_path)
    df = df.fillna("")

    for _, row in df.iterrows():
        city = City(
            city=row["city"],
            city_ascii=row["city_ascii"],
            lat=row["lat"],
            lng=row["lng"],
            country=row["country"],
            admin_name=row["admin_name"],
        )
        for continent, countries in continent_country_map.items():
            if city.country in countries:
                city.region = continent
                break

        session.add(city)
    await session.commit()


async def main():
    async with AsyncSessionLocal() as session:
        await populate_cities_from_csv(
            settings.PROJECT_ROOT / "data" / "worldcities.csv", session
        )


if __name__ == "__main__":
    asyncio.run(main())
