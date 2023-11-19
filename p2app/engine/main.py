# p2app/engine/main.py
#
# ICS 33 Spring 2023
# Project 2: Learning to Fly
#
# Helen Chau
# 84334175
# chauh4@uci.edu
#
# An object that represents the engine of the application.
#
# This is the outermost layer of the part of the program that you'll need to build,
# which means that YOU WILL DEFINITELY NEED TO MAKE CHANGES TO THIS FILE.

import sqlite3
import p2app.events as event_app
import p2app.views as views
from pathlib import Path

class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        self.cursor = None
        self.connection = None
        pass

    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        # This is a way to write a generator function that always yields zero values.
        # You'll want to remove this and replace it with your own code, once you start
        # writing your engine, but this at least allows the program to run.
        if isinstance(event, views.main.OpenDatabaseEvent):
            try:
                if event.path().suffix == ".db":
                    self.connection = sqlite3.connect(Path(event.path()), isolation_level = None)
                    self.connection.commit()
                    self.cursor = self.connection.cursor()
                    self.cursor.execute('PRAGMA foreign_keys = ON;')
                    if self.database_checker() is True:
                        yield event_app.DatabaseOpenedEvent(Path(event.path()))
                    else:
                        raise sqlite3.DatabaseError
                else:
                    raise sqlite3.DatabaseError
            except sqlite3.DatabaseError:
                yield event_app.DatabaseOpenFailedEvent("Invalid database file")
        elif isinstance(event, views.main.CloseDatabaseEvent):
            yield event_app.DatabaseClosedEvent()
        elif isinstance(event, views.main.QuitInitiatedEvent):
            yield event_app.EndApplicationEvent()
        elif isinstance(event, views.main.StartContinentSearchEvent):
            try:
                self.cursor.execute("SELECT * FROM continent WHERE continent_code = ? OR name = ?",
                                     (event.continent_code(), event.name()))

                results = self.cursor.fetchall()
                for result in results:
                    if result is not None:
                        con_result = event_app.Continent(result[0],
                                            result[1],
                                            result[2])
                        yield event_app.ContinentSearchResultEvent(con_result)
            except Exception:
                yield event_app.ErrorEvent("Search for continent failed")
        elif isinstance(event, views.main.LoadContinentEvent):
            try:
                self.cursor.execute("SELECT * FROM continent WHERE continent_id = ?",
                                     (event.continent_id(),))

                results = self.cursor.fetchall()
                for result in results:
                    if result is not None:
                        con_result = event_app.Continent(result[0],
                                            result[1],
                                            result[2])
                        yield event_app.ContinentLoadedEvent(con_result)
            except Exception:
                yield event_app.ErrorEvent("Loading Continent failed")
        elif isinstance(event, views.main.SaveNewContinentEvent):
            try:
                info = event.continent()
                self.cursor.execute(f"INSERT INTO continent (continent_code, name) "
                                    f"VALUES (?, ?)", (info.continent_code, info.name))
                self.connection.commit()
                yield event_app.ContinentSavedEvent(event.continent())
            except sqlite3.IntegrityError as sq_error:
                yield event_app.SaveContinentFailedEvent(sq_error.args)
        elif isinstance(event, views.main.SaveContinentEvent):
            try:
                info = event.continent()
                if type(info.continent_id) == int:
                    self.cursor.execute(f"UPDATE continent "
                                        f"SET name = ?, "
                                        f"continent_code = ? "
                                        f"WHERE continent_id = ?",
                                        (info.name, info.continent_code, info.continent_id))
                    self.connection.commit()
                    yield event_app.ContinentSavedEvent(info)
                else:
                    raise ValueError
            except sqlite3.IntegrityError as sq_error:
                yield event_app.SaveContinentFailedEvent(sq_error.args)
            except ValueError:
                yield event_app.SaveContinentFailedEvent("Continent id must be valid integers")
        elif isinstance(event, views.main.StartCountrySearchEvent):
            try:
                self.cursor.execute("SELECT * FROM country WHERE country_code = ? OR name = ?",
                                     (event.country_code(), event.name()))

                results = self.cursor.fetchall()
                for result in results:
                    if result is not None:
                        con_result = event_app.Country(result[0],
                                                    result[1],
                                                    result[2],
                                                    result[3],
                                                    result[4],
                                                    result[5])
                        yield event_app.CountrySearchResultEvent(con_result)
            except Exception:
                yield event_app.ErrorEvent("Searching for country failed")
        elif isinstance(event, views.main.LoadCountryEvent):
            try:
                self.cursor.execute("SELECT * FROM country WHERE country_id = ?",
                                     (event.country_id(),))

                results = self.cursor.fetchall()
                for result in results:
                    if result is not None:
                        con_result = event_app.Country(result[0],
                                            result[1],
                                            result[2],
                                            result[3],
                                            result[4],
                                            result[5])
                        yield event_app.CountryLoadedEvent(con_result)
            except Exception:
                yield event_app.ErrorEvent("Loading country failed")
        elif isinstance(event, views.main.SaveNewCountryEvent):
            try:
                info = event.country()
                if  type(info.continent_id) == int:
                    self.cursor.execute("INSERT INTO country (country_code, name,"
                                        " continent_id, wikipedia_link, keywords) "
                                        "VALUES (?, ?, ?, ?, ?)",
                                        (info.country_code, info.name, info.continent_id,
                                          info.wikipedia_link, info.keywords))
                    self.connection.commit()
                    yield event_app.CountrySavedEvent(info)
                else:
                    raise ValueError
            except sqlite3.IntegrityError as sq_error:
                yield event_app.SaveCountryFailedEvent(sq_error.args)
            except ValueError:
                yield event_app.SaveCountryFailedEvent("Continent id must be valid integers")
        elif isinstance(event, views.main.SaveCountryEvent):
            try:
                info = event.country()
                if type(info.continent_id) == int:
                    self.cursor.execute("UPDATE country "
                                        "SET name = ?, country_code = ?,"
                                        " wikipedia_link = ?, keywords = ? "
                                        "WHERE country_id = ?",
                                        (info.name, info.country_code, info.wikipedia_link,
                                          info.keywords, info.country_id))
                    self.connection.commit()
                    yield event_app.CountrySavedEvent(info)
                else:
                    raise ValueError
            except sqlite3.IntegrityError as sq_error:
                yield event_app.SaveCountryFailedEvent(sq_error.args)
            except ValueError:
                yield event_app.SaveCountryFailedEvent("Continent id must be valid integers")
        elif isinstance(event, views.main.StartRegionSearchEvent):
            try:
                self.cursor.execute("SELECT * FROM region "
                                    "WHERE region_code = ? OR name = ? OR local_code = ?",
                                    (event.region_code(), event.name(), event.local_code()))
                results = self.cursor.fetchall()
                for result in results:
                    if result is not None:
                        con_result = event_app.Region(result[0],
                                                    result[1],
                                                    result[2],
                                                    result[3],
                                                    result[4],
                                                    result[5],
                                                    result[6],
                                                    result[7])
                        yield event_app.RegionSearchResultEvent(con_result)
            except Exception:
                yield event_app.ErrorEvent("Searching for region failed")
        elif isinstance(event, views.main.LoadRegionEvent):
            try:
                self.cursor.execute("SELECT * FROM region WHERE region_id = ?",
                                     (event.region_id(),))
                results = self.cursor.fetchall()
                for result in results:
                    if result is not None:
                        con_result = event_app.Region(result[0],
                                                    result[1],
                                                    result[2],
                                                    result[3],
                                                    result[4],
                                                    result[5],
                                                    result[6],
                                                    result[7])
                        yield event_app.RegionLoadedEvent(con_result)
            except Exception:
                yield event_app.ErrorEvent("Loading region failed")
        elif isinstance(event, views.main.SaveNewRegionEvent):
            try:
                info = event.region()
                if type(info.country_id) == int and type(info.continent_id) == int:
                    self.cursor.execute("INSERT INTO region (region_code, local_code, name,"
                                        "continent_id, country_id, wikipedia_link, keywords) "
                                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                                        (info.region_code, info.local_code, info.name,
                                          info.continent_id, info.country_id,
                                            info.wikipedia_link, info.keywords))
                    self.connection.commit()
                    yield event_app.RegionSavedEvent(info)
                else:
                    raise ValueError
            except sqlite3.IntegrityError as sq_error:
                yield event_app.SaveRegionFailedEvent(f"{sq_error.args}")
            except ValueError:
                yield event_app.SaveRegionFailedEvent("Continent id or country id must be valid integers")
        elif isinstance(event, views.main.SaveRegionEvent):
            try:
                info = event.region()
                if type(info.country_id) == int and type(info.continent_id) == int:
                    self.cursor.execute("UPDATE region "
                                        "SET region_code = ?, local_code = ?, name = ?,"
                                        " continent_id = ?, country_id = ?, wikipedia_link = ?, keywords = ? "
                                        "WHERE region_id = ?",
                                        (info.region_code, info.local_code, info.name, info.continent_id,
                                          info.country_id, info.wikipedia_link, info.keywords, info.region_id))
                    self.connection.commit()
                    yield event_app.RegionSavedEvent(info)
                else:
                    raise ValueError
            except sqlite3.IntegrityError as sq_error:
                yield event_app.SaveRegionFailedEvent(sq_error.args)
            except ValueError:
                yield event_app.SaveRegionFailedEvent("Continent id or country id must be valid integers")

    def database_checker(self):
        try:
            self.cursor.execute("SELECT * FROM continent WHERE name == 'Asia';")
            return True
        except Exception:
            return False
