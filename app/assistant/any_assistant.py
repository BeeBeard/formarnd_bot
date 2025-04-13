import pprint
import re
from typing import List, Union, Dict, Any
from aiogram.fsm.context import FSMContext


def get_int_from_str(text: str) -> Union[int, None]:
    _result = re.findall(r"\d+", text)
    if _result:
        return int(_result[-1])
    return None

async def print_state_data(state: FSMContext) -> Dict[str, Any]:
    data = await state.get_data()
    pprint.pprint(data)
    return data
