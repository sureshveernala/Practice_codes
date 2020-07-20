from unittest.mock import create_autospec, Mock
import pytest
import uuid
from django_swagger_utils.drf_server.exceptions import BadRequest, NotFound
from content_management.interactors.add_rough_solutions_interactor import \
    AddRoughSolutionsInteractor
from content_management.interactors.storage_interfaces.\
    rough_solution_storage_interface import RoughSolutionStorageInterface
from content_management.interactors.presenter_interfaces.\
    rough_solution_presenter_interface import \
    AddRoughSolutionsPresenterInterface
from content_management.interactors.storage_interfaces.\
    coding_question_storage_interface import CodingQuestionStorageInterface
from content_management.tests.factories.interactor_dtos import \
    SolutionDTOFactory



class TestAddRoughSolutions:

    @pytest.fixture
    def create_rough_solutions_for_interactor(self):
        SolutionDTOFactory.reset_sequence()
        solution_dtos = [
            SolutionDTOFactory(
                solution_id=uuid.UUID('c5aeeca0-e2bd-4dcb-bf14-634c17c6932b')
            ),
            SolutionDTOFactory(
                solution_id=None
            )
        ]
        return solution_dtos

    @pytest.fixture
    def create_rough_solutions_for_storage(self):
        SolutionDTOFactory.reset_sequence()
        solution_dtos = [
            SolutionDTOFactory(
                solution_id=uuid.UUID('c5aeeca0-e2bd-4dcb-bf14-634c17c6932b')
            ),
            SolutionDTOFactory(
                solution_id=uuid.UUID('c5aeeca0-e2bd-4dcb-bf14-634c17c6932b')
            )
        ]
        return solution_dtos

    def test_when_question_id_is_invalid_raises_error(
            self, create_rough_solutions_for_interactor
        ):
        # Arrange
        question_id = uuid.UUID('c5aeeca0-e2bd-4dcb-bf14-634c17c6932b')
        rough_solutions = create_rough_solutions_for_interactor
        rough_solution_storage = create_autospec(RoughSolutionStorageInterface)
        question_storage = create_autospec(CodingQuestionStorageInterface)
        presenter = create_autospec(AddRoughSolutionsPresenterInterface)
        interactor = AddRoughSolutionsInteractor(
            coding_question_storage=question_storage,
            rough_solution_storage=rough_solution_storage,
            presenter=presenter
        )
        question_storage.is_valid_question_id.return_value = False
        presenter.raise_invalid_question_exception_response.side_effect = \
            NotFound

        invalid_rough_solution_id = \
            uuid.UUID('c5aeeca0-e2bd-4dcb-bf14-634c17c6932b')
        # Act
        with pytest.raises(NotFound):
            interactor.add_solutions_wrapper(
                solution_dtos=rough_solutions,
                question_id=question_id
            )

        # Assert
        kwargs = presenter.raise_invalid_question_exception_response.\
            call_args.kwargs
        error = kwargs['error']
        assert error.question_id == question_id

    def test_when_solution_ids_is_invalid_raises_error(
            self, create_rough_solutions_for_interactor
        ):
        # Arrange
        question_id = uuid.UUID('c5aeeca0-e2bd-4dcb-bf14-634c17c6932b')
        rough_solutions = create_rough_solutions_for_interactor
        invalid_rough_solution_id = \
            uuid.UUID('c5aeeca0-e2bd-4dcb-bf14-634c17c6932b')
        rough_solution_storage = create_autospec(RoughSolutionStorageInterface)
        question_storage = create_autospec(CodingQuestionStorageInterface)
        presenter = create_autospec(AddRoughSolutionsPresenterInterface)
        interactor = AddRoughSolutionsInteractor(
            coding_question_storage=question_storage,
            rough_solution_storage=rough_solution_storage,
            presenter=presenter
        )
        rough_solution_storage.get_question_rough_solution_ids.return_value = \
            [uuid.UUID('c5aeeca0-e2bd-4dcb-bf14-634c17c6932c')]
        presenter.raise_invalid_solutions_exception_response.side_effect = \
            BadRequest

        # Act
        with pytest.raises(BadRequest):
            interactor.add_solutions_wrapper(
                solution_dtos=rough_solutions,
                question_id=question_id
            )

        # Assert
        kwargs = presenter.raise_invalid_solutions_exception_response.\
            call_args.kwargs
        error = kwargs['error']
        assert error.solution_ids == [invalid_rough_solution_id]

    def test_with_valid_details_return_response_with_rough_solutions_details(
            self,
            create_rough_solutions_for_interactor,
            create_rough_solutions_for_storage
        ):
        # Arrange
        question_id = uuid.UUID('c5aeeca0-e2bd-4dcb-bf14-634c17c6932b')
        rough_solutions = create_rough_solutions_for_interactor
        expected_rough_solutions = create_rough_solutions_for_storage
        rough_solution_storage = create_autospec(RoughSolutionStorageInterface)
        question_storage = create_autospec(CodingQuestionStorageInterface)
        presenter = create_autospec(AddRoughSolutionsPresenterInterface)
        interactor = AddRoughSolutionsInteractor(
            coding_question_storage=question_storage,
            rough_solution_storage=rough_solution_storage,
            presenter=presenter
        )
        presenter_mock_response = Mock()
        rough_solution_storage.get_question_rough_solution_ids.return_value = \
            [uuid.UUID('c5aeeca0-e2bd-4dcb-bf14-634c17c6932b')]
        rough_solution_storage.get_question_rough_solution_dtos.return_value = \
            expected_rough_solutions
        presenter.get_add_solutions_response.return_value = \
            presenter_mock_response

        # Act
        response = interactor.add_solutions_wrapper(
            solution_dtos=rough_solutions,
            question_id=question_id
        )

        # Assert
        rough_solution_storage.create_rough_solutions.assert_called_once_with(
            rough_solution_dtos=rough_solutions[1:], question_id=question_id
        )
        rough_solution_storage.update_rough_solutions.assert_called_once_with(
            rough_solution_dtos=rough_solutions[:1],
            rough_solution_ids=[uuid.UUID('c5aeeca0-e2bd-4dcb-bf14-634c17c6932b')]
        )
        rough_solution_storage.get_question_rough_solution_dtos.\
            assert_called_once_with(question_id=question_id)
        presenter.get_add_solutions_response.assert_called_once_with(
            solution_dtos=expected_rough_solutions
        )
        assert response == presenter_mock_response
