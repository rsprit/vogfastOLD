import sys
from fastapi import Query, Path, HTTPException
from typing import Optional, Set, List
from .functionality import VogService, find_vogs_by_uid, get_proteins, get_vogs, get_species, find_species_by_id, \
    find_proteins_by_id
from .database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI
from .schemas import VOG_profile, Protein_profile, Filter, VOG_UID, Species_ID, Species_profile, ProteinID
from . import models

api = FastAPI()
svc = VogService('data')


# Dependency. Connect to the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@api.get("/")
async def root():
    return {"message": "Welcome to VOGDB-API"}


@api.get("/vsearch/species/",
         response_model=List[Species_ID])
def search_species(db: Session = Depends(get_db),
                   ids: Optional[Set[int]] = Query(None),
                   name: Optional[str] = None,
                   phage: Optional[bool] = None,
                   source: Optional[str] = None,
                   version: Optional[int] = None):
    """
    This functions searches a database and returns a list of species IDs for records in that database
    which meet the search criteria.
    :return:
    """
    species = get_species(db, models.Species_profile.taxon_id, ids, name, phage, source, version)

    if not species:
        raise HTTPException(status_code=404, detail="No Species match the search criteria.")
    return species


@api.get("/vsummary/species/",
         response_model=List[Species_profile])
async def get_summary(taxon_id: Optional[List[int]] = Query(None), db: Session = Depends(get_db)):
    """
    This function returns Species summaries for a list of taxon ids
    :param taxon_id: Taxon ID
    :param db: database session dependency
    :return: Species summary
    """

    species_summary = find_species_by_id(db, taxon_id)

    if not species_summary:
        raise HTTPException(status_code=404, detail="No matching Species found")

    return species_summary


@api.get("/vsearch/vog/",
         response_model=List[VOG_UID])
def search_vog(db: Session = Depends(get_db),
               id: Optional[Set[str]] = Query(None),
               pmin: Optional[int] = None,
               pmax: Optional[int] = None,
               smax: Optional[int] = None,
               smin: Optional[int] = None,
               functional_category: Optional[Set[str]] = Query(None),
               consensus_function: Optional[Set[str]] = Query(None),
               mingLCA: Optional[int] = None,
               maxgLCA: Optional[int] = None,
               mingGLCA: Optional[int] = None,
               maxgGLCA: Optional[int] = None,
               ancestors: Optional[Set[str]] = Query(None),
               h_stringency: Optional[bool] = None,
               m_stringency: Optional[bool] = None,
               l_stringency: Optional[bool] = None,
               virus_specific: Optional[bool] = None,
               phages_nonphages: Optional[str] = None,
               proteins: Optional[Set[str]] = Query(None),
               species: Optional[Set[str]] = Query(None),
               ):
    """
    This functions searches a database and returns a list of vog unique identifiers (UIDs) for records in that database
    which meet the search criteria.
    :return:
    """

    vogs = get_vogs(db, models.VOG_profile.id, id, pmin, pmax, smax, smin, functional_category, consensus_function,
                    mingLCA, maxgLCA, mingGLCA, maxgGLCA,
                    ancestors, h_stringency, m_stringency, l_stringency, virus_specific, phages_nonphages, proteins,
                    species)

    if not vogs:
        raise HTTPException(status_code=404, detail="No VOGs match the search criteria.")
    return vogs


@api.get("/vsummary/vog/",
         response_model=List[VOG_profile])
async def get_summary(uid: List[str] = Query(None), db: Session = Depends(get_db)):
    """
    This function returns vog summaries for a list of unique identifiers (UIDs)
    :param uid: VOGID
    :param db: database session dependency
    :return: vog summary
    """

    vog_summary = find_vogs_by_uid(db, uid)

    if not vog_summary:
        raise HTTPException(status_code=404, detail="No matching VOGs found")

    return vog_summary


@api.get("/vsearch/protein/",
         response_model=List[ProteinID])
async def search_protein(db: Session = Depends(get_db),
                         species_name: Optional[Set[str]] = Query(None),
                         taxon_id: Optional[Set[int]] = Query(None),
                         VOG_id: Optional[Set[str]] = Query(None)):
    proteins = get_proteins(db, models.Protein_profile.protein_id, species_name, taxon_id, VOG_id)
    if not proteins:
        raise HTTPException(status_code=404, detail="No matching Proteins found")

    return proteins


@api.get("/vsummary/protein/",
         response_model=List[Protein_profile])
async def get_summary(pids: List[str] = Query(None), db: Session = Depends(get_db)):
    """
    This function returns protein summaries for a list of Protein identifiers (pids)
    :param pids: proteinID
    :param db: database session dependency
    :return: protein summary
    """

    protein_summary = find_proteins_by_id(db, pids)

    if not protein_summary:
        raise HTTPException(status_code=404, detail="No matching Proteins found")

    return protein_summary


@api.get("/vfetch/vog/")
async def fetch_vog(uid: List[str] = Query(None), db: Session = Depends(get_db)):
    """
    This function returns vog data for a list of unique identifiers (UIDs)
    :param uid: VOGID
    :param db: database session dependency
    :return: vog data (HMM profile, MSE...)
    """

    # ToDo: implement...

    return 0



# OLD
#
# @api.get("/vog_profile1/", response_model=List[VOG_profile])
# def read_vog(ids: Optional[List[str]] = Query(None), db: Session = Depends(get_db)):
#     """This function takes a list of VOGids and returns all the matching VOG_profiles
#     """
#     vogs = find_vogs_by_uid(db, ids)
#
#     if not vogs:
#         raise HTTPException(status_code=404, detail="No VOGs found")
#     return vogs
#
#
# # VOG FILTERING:
# @api.get("/vog_filter/", response_model=List[VOG_profile])
# def vog_filter(db: Session = Depends(get_db), names: Optional[Set[str]] = Query(None),
#                fct_description: Optional[Set[str]] = Query(None),
#                fct_category: Optional[Set[str]] = Query(None), gmin: Optional[int] = None, gmax: Optional[int] = None,
#                pmin: Optional[int] = None, pmax: Optional[int] = None, species: Optional[Set[str]] = Query(None),
#                protein_names: Optional[Set[str]] = Query(None), mingLCA: Optional[int] = None,
#                maxgLCA: Optional[int] = None,
#                mingGLCA: Optional[int] = None, maxgGLCA: Optional[int] = None,
#                ancestors: Optional[Set[str]] = Query(None),
#                h_stringency: Optional[bool] = None, m_stringency: Optional[bool] = None,
#                l_stringency: Optional[bool] = None,
#                virus_spec: Optional[bool] = None):
#     vogs = vog_get(db, names, fct_description, fct_category, gmin, gmax, pmin, pmax, species, protein_names, mingLCA, maxgLCA, mingGLCA, maxgGLCA,
#                       ancestors, h_stringency, m_stringency, l_stringency, virus_spec)
#     if not vogs:
#         raise HTTPException(status_code=404, detail="No VOGs found")
#     return vogs
#
#
#
# @api.get("/protein_profile1/", response_model=List[Protein_profile])
# def read_protein(species: str = Query(None), db: Session = Depends(get_db)):
#     """This function takes only one species and returns all protein profiles associated with this species/family
#     """
#
#     proteins = get_proteins(db, species)
#     if not proteins:
#         raise HTTPException(status_code=404, detail="User not found")
#     return proteins
#
#
# @api.get("/species")
# async def get_species(name: Optional[Set[str]] = Query(None), id: Optional[Set[int]] = Query(None),
#                       phage: Optional[bool] = None, source: Optional[str] = None):
#     response = list(svc.species.search(name=name, ids=id, phage=phage, source=source))
#     if not response:
#         return {"message": "Nothing could be found for your search options."}
#     return response
#
#
# @api.get("/vog")
# async def get_vogs(
#         names: Optional[Set[str]] = Query(None), fct_description: Optional[Set[str]] = Query(None),
#         fct_category: Optional[Set[str]] = Query(None), gmin: Optional[int] = None, gmax: Optional[int] = None,
#         pmin: Optional[int] = None, pmax: Optional[int] = None, species: Optional[Set[str]] = Query(None),
#         protein_names: Optional[Set[str]] = Query(None), mingLCA: Optional[int] = None, maxgLCA: Optional[int] = None,
#         mingGLCA: Optional[int] = None, maxgGLCA: Optional[int] = None, ancestors: Optional[Set[str]] = Query(None),
#         h_stringency: Optional[bool] = None, m_stringency: Optional[bool] = None, l_stringency: Optional[bool] = None,
#         virus_spec: Optional[bool] = None):
#     response = list(svc.groups.search(names=names, fct_description=fct_description, fct_category=fct_category,
#                                       gmin=gmin, gmax=gmax, pmin=pmin, pmax=pmax, species=species,
#                                       protein_names=protein_names, mingLCA=mingLCA, maxgLCA=maxgLCA, mingGLCA=mingGLCA,
#                                       maxgGLCA=maxgGLCA, ancestors=ancestors, h_stringency=h_stringency,
#                                       m_stringency=m_stringency, l_stringency=l_stringency, virus_spec=virus_spec))
#     if not response:
#         return {"message": "Nothing could be found for your search options."}
#     return response
#
#
# @api.post("/filter/")
# async def create_filter(paras: Filter):
#     print("filter")
#     #
#     # finds aufrufen...
#     return paras
#
#
# searches = {
#     "search1": {"sid": 1002724},
#     "search2": {"sn": "India", "phage": True}
# }

# @api.get("/vog_filtering/{Filter: paras}", response_model=List[VOG])


# @api.get("/species_filtering/", response_model=List[Species])

# @api.get("/protein_filtering/", response_model=List[Protein])
