import abc
import uuid
from content_management.interactors.storage_interfaces.\
    coding_question_storage_interface import CodingQuestionStorageInterface
from typing import List, Tuple
from content_management.interactors.dtos import SolutionDTO
from content_management.interactors.mixins.validation_mixin\
    import ValidationMixin
from content_management.exceptions.custom_exceptions import InvalidQuestionId,\
    InvalidSolutionIds


class BaseAddSolutionsInteractor(ValidationMixin):
    def __init__(
            self,
            coding_question_storage: CodingQuestionStorageInterface
        ):
        self.coding_question_storage = coding_question_storage


    def add_solutions_wrapper(
            self, solution_dtos: List[SolutionDTO], question_id: uuid.UUID
        ):
        try:
            new_solution_dtos = self.add_solutions(
                solution_dtos=solution_dtos, question_id=question_id
            )
        except InvalidQuestionId as error:
            return self.presenter.raise_invalid_question_exception_response(
                error=error
            )
        except InvalidSolutionIds as error:
            return self.presenter.raise_invalid_solutions_exception_response(
                error=error
            )

        response = self.presenter.get_add_solutions_response(
            solution_dtos=new_solution_dtos
        )
        return response


    def add_solutions(
            self, solution_dtos: List[SolutionDTO], question_id: uuid.UUID
        ):
        self._validate_question_id(question_id=question_id)
        have_to_update_solution_dtos, have_to_update_solution_ids = \
            self._get_updating_solution_ids_and_dtos_list(
                solution_dtos=solution_dtos
            )

        self._valiadate_solutions(
            solution_ids=have_to_update_solution_ids, question_id=question_id
        )

        self._update_solutions(
            solution_ids=have_to_update_solution_ids,
            solution_dtos=have_to_update_solution_dtos,
        )

        have_to_create_solutions_list = \
            self._get_have_to_create_solutions_list(
                solution_dtos=solution_dtos
            )
        self._create_new_solutions(
            solution_dtos=have_to_create_solutions_list,
            question_id=question_id
        )

        new_solution_dtos = self._get_solutions(question_id=question_id)

        return new_solution_dtos

    def _get_updating_solution_ids_and_dtos_list(
            self, solution_dtos: List[SolutionDTO]
        ) -> Tuple:
        have_to_update_solution_dtos = []
        have_to_update_solution_ids = []
        for solution_dto in solution_dtos:
            is_update = solution_dto.solution_id
            if is_update:
                have_to_update_solution_ids.append(solution_dto.solution_id)
                have_to_update_solution_dtos.append(solution_dto)
        return have_to_update_solution_dtos, have_to_update_solution_ids

    def _get_have_to_create_solutions_list(
            self, solution_dtos: List[SolutionDTO]
        ):
        have_to_create_solutions_list = [
            solution_dto
            for solution_dto in solution_dtos
            if solution_dto.solution_id is None
        ]
        return have_to_create_solutions_list

    def _valiadate_solutions(
            self, solution_ids: List[uuid.UUID], question_id: uuid.UUID
        ):
        invalid_solution_ids = \
            self._invalid_solution_ids(
                solution_ids=solution_ids, question_id=question_id
            )
        if invalid_solution_ids:
            raise InvalidSolutionIds(solution_ids=solution_ids)

    def _invalid_solution_ids(
            self, solution_ids: List[uuid.UUID], question_id: uuid.UUID
        ):
        total_question_solution_ids = self._get_question_solution_ids(
            question_id=question_id
        )
        invalid_solution_ids = [
            solution_id
            for solution_id in solution_ids
            if solution_id not in total_question_solution_ids
        ]
        return invalid_solution_ids

    @abc.abstractmethod
    def _get_question_solution_ids(
            self, question_id: uuid.UUID
        ) -> List[uuid.UUID]:
        pass

    @abc.abstractmethod
    def _create_new_solutions(
            self, solution_dtos: List[SolutionDTO], question_id: uuid.UUID
        ):
        pass

    @abc.abstractmethod
    def _update_solutions(
            self, solution_ids: List[uuid.UUID],
            solution_dtos: List[SolutionDTO]
        ):
        pass

    @abc.abstractmethod
    def _get_solutions(self, question_id: uuid.UUID):
        pass
