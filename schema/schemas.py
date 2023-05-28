datasource_schema = """
CREATE TABLE "DataSource" (
  "datasource_id" varchar(255),
  "name" varchar(255),
  "publisher" varchar(255),
  "published" timestamp,
  "URL" varchar(255),
  "created" timestamp,
  "last_updated" timestamp,
  PRIMARY KEY ("datasource_id"),
  CONSTRAINT "FK_DataSource.publisher"
    FOREIGN KEY ("publisher")
      REFERENCES "Publisher"("id")
)
"""
actor_schema = """
CREATE TABLE "Actor" (
  "actor_id" varchar(255), /* Unique identifier for the Actor; ISO-3166, UN/LOCODE, other */
  "type" varchar(255), /* One of: planet, country, adm1, city, organization, site */
  "name" varchar(255), /* Default; see ActorName for alternates and languages */
  "icon" varchar(255), /* URI of a square, small avatar icon, like a flag or logo */
  "hq" varchar(255),
  "is_part_of" varchar(255), /* Where this actor is physically */
  "is_owned_by" varchar(255), /* Only for sites, which company owns them */
  "datasource_id" varchar(255), /* Where the record came from */
  "created" timestamp,
  "last_updated" timestamp,
  PRIMARY KEY ("actor_id"),
  CONSTRAINT "FK_Actor.is_owned_by"
    FOREIGN KEY ("is_owned_by")
      REFERENCES "Actor"("actor_id"),
  CONSTRAINT "FK_Actor.is_part_of"
    FOREIGN KEY ("is_part_of")
      REFERENCES "Actor"("actor_id"),
  CONSTRAINT "FK_Actor.datasource_id"
    FOREIGN KEY ("datasource_id")
      REFERENCES "DataSource"("datasource_id")
);


"""

emissions_agg_schema = """
CREATE TABLE "EmissionsAgg" (
  "emissions_id" varchar(255), /* Unique identifier for this record */
  "actor_id" varchar(255), /* Responsible party for the emissions */
  "year" int, /* Year of emissions, YYYY */
  "total_emissions" bigint, /* Integer value of tonnes of CO2 equivalent */
  "methodology_id" varchar(255), /* Methodology used */
  "datasource_id" varchar(255), /* Source for the data */
  "created" timestamp,
  "last_updated" timestamp,
  PRIMARY KEY ("emissions_id"),
  CONSTRAINT "FK_EmissionsAgg.actor_id"
    FOREIGN KEY ("actor_id")
      REFERENCES "Actor"("actor_id"),
  CONSTRAINT "FK_EmissionsAgg.methodology_id"
    FOREIGN KEY ("methodology_id")
      REFERENCES "Methodology"("methodology_id"),
  CONSTRAINT "FK_EmissionsAgg.datasource_id"
    FOREIGN KEY ("datasource_id")
      REFERENCES "DataSource"("datasource_id")
);

"""

target_schema = """
CREATE TABLE "Target" (
  "target_id" varchar(255), /* Unique identifier for this target */
  "actor_id" varchar(255), /* Actor responsible for the target */
  "target_type" varchar(255),
  "baseline_year" int, /* Year of comparison, YYYY */
  "target_year" int, /* Year of completion, YYYY */
  "baseline_value" bigint, /* Value of comparison */
  "target_value" bigint, /* Value of target */
  "target_unit" varchar(255), /* Unit comparison; tonnes of CO2, percent, ? */
  "bau_value" int, /* ? */
  "is_net_zero" boolean, /* Will this get them to net zero? */
  "percent_achieved" int, /* ? */
  "URL" varchar(255), /* URL of a human-readable document on the target. */
  "summary" varchar(255), /* short summary in English of the target. */
  "datasource_id" varchar(255), /* Source of this data */
  "created" timestamp,
  "last_updated" timestamp,
  PRIMARY KEY ("target_id"),
  CONSTRAINT "FK_Target.actor_id"
    FOREIGN KEY ("actor_id")
      REFERENCES "Actor"("actor_id"),
  CONSTRAINT "FK_Target.datasource_id"
    FOREIGN KEY ("datasource_id")
      REFERENCES "DataSource"("datasource_id")
);

"""

actions_schema = """

CREATE TABLE "Action" (
  "action_id" varchar(255),
  "actor_id" varchar(255),
  "action_type" varchar(255),
  "sector" varchar(255),
  "year" int,
  "description" varchar(255),
  "emissions_reductions" int,
  "percent_achieved" int,
  "datasource_id" varchar(255),
  "created" timestamp,
  "last_updated" timestamp,
  PRIMARY KEY ("action_id"),
  CONSTRAINT "FK_Action.actor_id"
    FOREIGN KEY ("actor_id")
      REFERENCES "Actor"("actor_id"),
);

"""
