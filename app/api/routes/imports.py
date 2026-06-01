from io import StringIO

from fastapi import APIRouter, UploadFile, Depends

from app.core.dependencies import get_import_service
from app.core.security import get_current_user
from app.models.user import User
from app.parsers.allegro_csv_parser import AllegroCSVParser
from app.services.import_service import ImportService

router = APIRouter(prefix="/imports")

@router.post('/')
async def import_csv(
        file: UploadFile,
        current_user: User = Depends(get_current_user),
        import_service: ImportService = Depends(get_import_service)
):
    contents = await file.read()

    csv_stream = StringIO(
        contents.decode("utf-8")
    )
    parser = AllegroCSVParser()

    parsed_data = parser.parse(csv_stream)

    result = import_service.import_data(
        parsed_data=parsed_data,
        user=current_user,
        filename=file.filename
    )

    return result