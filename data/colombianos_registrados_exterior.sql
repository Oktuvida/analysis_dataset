-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler version: 0.9.4
-- PostgreSQL version: 13.0
-- Project Site: pgmodeler.io
-- Model Author: ---

-- Database creation must be performed outside a multi lined SQL file. 
-- These commands were put in this file only as a convenience.
-- 
-- object: colombianos_registrados_exterior | type: DATABASE --
-- DROP DATABASE IF EXISTS colombianos_registrados_exterior;
CREATE DATABASE colombianos_registrados_exterior;
-- ddl-end --

\connect colombianos_registrados_exterior;

-- object: public."Pais" | type: TABLE --
-- DROP TABLE IF EXISTS public."Pais" CASCADE;
CREATE TABLE public."Pais" (
	id integer NOT NULL,
	"id_Continente" integer,
	codigo varchar(3),
	nombre text,
	CONSTRAINT "Pais_pk" PRIMARY KEY (id)
);
-- ddl-end --
ALTER TABLE public."Pais" OWNER TO postgres;
-- ddl-end --

-- object: public.location | type: TYPE --
-- DROP TYPE IF EXISTS public.location CASCADE;
CREATE TYPE public.location AS
(
 latitude float8,
 longitude float8
);
-- ddl-end --
ALTER TYPE public.location OWNER TO postgres;
-- ddl-end --

-- object: public."OficinaRegistro" | type: TABLE --
-- DROP TABLE IF EXISTS public."OficinaRegistro" CASCADE;
CREATE TABLE public."OficinaRegistro" (
	id integer NOT NULL,
	"id_Pais" integer,
	nombre text,
	ubicacion public.location,
	CONSTRAINT "OficinaRegistro_pk" PRIMARY KEY (id)
);
-- ddl-end --
ALTER TABLE public."OficinaRegistro" OWNER TO postgres;
-- ddl-end --

-- object: "Pais_fk" | type: CONSTRAINT --
-- ALTER TABLE public."OficinaRegistro" DROP CONSTRAINT IF EXISTS "Pais_fk" CASCADE;
ALTER TABLE public."OficinaRegistro" ADD CONSTRAINT "Pais_fk" FOREIGN KEY ("id_Pais")
REFERENCES public."Pais" (id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: public."DescripcionDemografica" | type: TABLE --
-- DROP TABLE IF EXISTS public."DescripcionDemografica" CASCADE;
CREATE TABLE public."DescripcionDemografica" (
	id integer NOT NULL,
	"id_OficinaRegistro" integer,
	"id_NivelAcademico" integer,
	"id_Especializacion" integer,
	edad smallint,
	genero text,
	estatura integer,
	cantidad_personas smallint,
	CONSTRAINT "DescripcionDemografica_pk" PRIMARY KEY (id)
);
-- ddl-end --
ALTER TABLE public."DescripcionDemografica" OWNER TO postgres;
-- ddl-end --

-- object: "OficinaRegistro_fk" | type: CONSTRAINT --
-- ALTER TABLE public."DescripcionDemografica" DROP CONSTRAINT IF EXISTS "OficinaRegistro_fk" CASCADE;
ALTER TABLE public."DescripcionDemografica" ADD CONSTRAINT "OficinaRegistro_fk" FOREIGN KEY ("id_OficinaRegistro")
REFERENCES public."OficinaRegistro" (id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: public."Continente" | type: TABLE --
-- DROP TABLE IF EXISTS public."Continente" CASCADE;
CREATE TABLE public."Continente" (
	id integer NOT NULL,
	codigo varchar(2),
	nombre text,
	CONSTRAINT "Continente_pk" PRIMARY KEY (id)
);
-- ddl-end --
ALTER TABLE public."Continente" OWNER TO postgres;
-- ddl-end --

-- object: "Continente_fk" | type: CONSTRAINT --
-- ALTER TABLE public."Pais" DROP CONSTRAINT IF EXISTS "Continente_fk" CASCADE;
ALTER TABLE public."Pais" ADD CONSTRAINT "Continente_fk" FOREIGN KEY ("id_Continente")
REFERENCES public."Continente" (id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: public."NivelAcademico" | type: TABLE --
-- DROP TABLE IF EXISTS public."NivelAcademico" CASCADE;
CREATE TABLE public."NivelAcademico" (
	id integer NOT NULL,
	nombre text,
	CONSTRAINT "NivelAcademico_pk" PRIMARY KEY (id)
);
-- ddl-end --
ALTER TABLE public."NivelAcademico" OWNER TO postgres;
-- ddl-end --

-- object: "NivelAcademico_fk" | type: CONSTRAINT --
-- ALTER TABLE public."DescripcionDemografica" DROP CONSTRAINT IF EXISTS "NivelAcademico_fk" CASCADE;
ALTER TABLE public."DescripcionDemografica" ADD CONSTRAINT "NivelAcademico_fk" FOREIGN KEY ("id_NivelAcademico")
REFERENCES public."NivelAcademico" (id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: public."AreaConocimiento" | type: TABLE --
-- DROP TABLE IF EXISTS public."AreaConocimiento" CASCADE;
CREATE TABLE public."AreaConocimiento" (
	id integer NOT NULL,
	nombre text,
	CONSTRAINT "AreaConocimiento_pk" PRIMARY KEY (id)
);
-- ddl-end --
ALTER TABLE public."AreaConocimiento" OWNER TO postgres;
-- ddl-end --

-- object: public."Especializacion" | type: TABLE --
-- DROP TABLE IF EXISTS public."Especializacion" CASCADE;
CREATE TABLE public."Especializacion" (
	id integer NOT NULL,
	nombre text,
	"id_AreaConocimiento" integer,
	CONSTRAINT "Especializacion_pk" PRIMARY KEY (id)
);
-- ddl-end --
ALTER TABLE public."Especializacion" OWNER TO postgres;
-- ddl-end --

-- object: "Especializacion_fk" | type: CONSTRAINT --
-- ALTER TABLE public."DescripcionDemografica" DROP CONSTRAINT IF EXISTS "Especializacion_fk" CASCADE;
ALTER TABLE public."DescripcionDemografica" ADD CONSTRAINT "Especializacion_fk" FOREIGN KEY ("id_Especializacion")
REFERENCES public."Especializacion" (id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: "AreaConocimiento_fk" | type: CONSTRAINT --
-- ALTER TABLE public."Especializacion" DROP CONSTRAINT IF EXISTS "AreaConocimiento_fk" CASCADE;
ALTER TABLE public."Especializacion" ADD CONSTRAINT "AreaConocimiento_fk" FOREIGN KEY ("id_AreaConocimiento")
REFERENCES public."AreaConocimiento" (id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --


