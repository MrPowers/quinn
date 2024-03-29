from __future__ import annotations

import copy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import DataFrame
    from pyspark.sql.types import StructType


class DataFrameMissingColumnError(ValueError):
    """Raise this when there's a DataFrame column error."""


class DataFrameMissingStructFieldError(ValueError):
    """Raise this when there's a DataFrame column error."""


class DataFrameProhibitedColumnError(ValueError):
    """Raise this when a DataFrame includes prohibited columns."""


def validate_presence_of_columns(df: DataFrame, required_col_names: list[str]) -> None:
    """Validate the presence of column names in a DataFrame.

    :param df: A spark DataFrame.
    :type df: DataFrame`
    :param required_col_names: List of the required column names for the DataFrame.
    :type required_col_names: :py:class:`list` of :py:class:`str`
    :return: None.
    :raises DataFrameMissingColumnError: if any of the requested column names are
    not present in the DataFrame.
    """
    all_col_names = df.columns
    missing_col_names = [x for x in required_col_names if x not in all_col_names]
    error_message = f"The {missing_col_names} columns are not included in the DataFrame with the following columns {all_col_names}"
    if missing_col_names:
        raise DataFrameMissingColumnError(error_message)
    
def validate_schema(
    required_schema: StructType, 
    ignore_nullable: bool = False, 
    _df: DataFrame = None
) -> function:
    """Function that validate if a given DataFrame has a given StructType as its schema.
    Implemented as a decorator factory so can be used both as a standalone function or as 
    a decorator to another function.

    :param required_schema: StructType required for the DataFrame
    :type required_schema: StructType
    :param ignore_nullable: (Optional) A flag for if nullable fields should be
    ignored during validation
    :type ignore_nullable: bool, optional
    :param _df: DataFrame to validate, mandatory when called as a function. Not required
    when called as a decorator
    :type _df: DataFrame

    :raises DataFrameMissingStructFieldError: if any StructFields from the required
    schema are not included in the DataFrame schema
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            df = func(*args, **kwargs)
            _all_struct_fields = copy.deepcopy(df.schema)
            _required_schema = copy.deepcopy(required_schema)

            if ignore_nullable:
                for x in _all_struct_fields:
                    x.nullable = None

                for x in _required_schema:
                    x.nullable = None

            missing_struct_fields = [x for x in _required_schema if x not in _all_struct_fields]
            error_message = f"The {missing_struct_fields} StructFields are not included in the DataFrame with the following StructFields {_all_struct_fields}"

            if missing_struct_fields:
                raise DataFrameMissingStructFieldError(error_message)
            else:
                print("Success! DataFrame matches the required schema!")

            return df
        return wrapper

    if _df is None:
        # This means the function is being used as a decorator
        return decorator
    else:
        # This means the function is being called directly with a DataFrame
        return decorator(lambda: _df)()


def validate_absence_of_columns(df: DataFrame, prohibited_col_names: list[str]) -> None:
    """Validate that none of the prohibited column names are present among specified DataFrame columns.

    :param df: DataFrame containing columns to be checked.
    :param prohibited_col_names: List of prohibited column names.
    :raises DataFrameProhibitedColumnError: If the prohibited column names are
    present among the specified DataFrame columns.
    """
    all_col_names = df.columns
    extra_col_names = [x for x in all_col_names if x in prohibited_col_names]
    error_message = f"The {extra_col_names} columns are not allowed to be included in the DataFrame with the following columns {all_col_names}"
    if extra_col_names:
        raise DataFrameProhibitedColumnError(error_message)
