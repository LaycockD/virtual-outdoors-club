/**
 * Manages the state for the GearPage, primarily.
 */

import Reflux from "reflux";
import GearService from "../../services/GearService";
import update from "immutability-helper";
import Constants from "../../constants/constants";
import { toast } from "react-toastify";
import moment from "moment";
import ReservationService from "../../services/ReservationService";

function gearCategorycompare(a, b) {
    // Use toUpperCase() to ignore character casing
    const nameA = a.name.toUpperCase(),
        nameB = b.name.toUpperCase();

    let comparison = 0;
    if (nameA > nameB) {
        comparison = 1;
    } else if (nameA < nameB) {
        comparison = -1;
    }
    return comparison;
}

function defaultState() {
    return {
        fetchedGearList: false, // initial check to fetch the gear list
        tabSelected: 1,
        error: false,
        errorMessage: "",
        upload: {
            gear: [],
            categories: [],
            warnings: [],
            error: "",
            results: {
                show: false,
                failed: []
            }
        },
        categoryDropdown: {
            categorySelected: ""
        },
        gearList: [],
        gearModal: {
            show: false,
            error: false,
            errorMessage: "",
            mode: null,
            id: null,
            expectedVersion: null,
            gearCode: "",
            depositFee: "",
            gearCategory: "",
            gearDescription: "",
            gearCondition: "",
            gearStatus: "",
            tabSelected: 1,
            gearHistory: [],
            gearReservationHistory: []
        },
        fetchedGearCategoryList: false,
        categoryList: [],
        categoryModal: {
            show: false,
            error: false,
            errorMessage: "",
            originalName: null,
            mode: null,
            category: ""
        },
        shoppingList: [],
        deleteGearModal: {
            id: null,
            show: false,
            error: false,
            errorMessage: ""
        },
        deleteGearCategoryModal: {
            name: null,
            show: false,
            error: false,
            errorMessage: ""
        },
        reserveGearForm: {
            show: false,
            error: false,
            errorMessage: "Reservation failed",
            items: [],
            email: "",
            licenseName: "",
            licenseAddress: "",
            startDate: null,
            endDate: null
        },
        checkoutDisabled: true,
        checkboxOptions: {
            RENTABLE: true,
            FLAGGED: true,
            NEEDS_REPAIR: true,
            DELETED: false
        },
        rentableList: [],
        conditionSelected: "",
        fetchedRentableGearList: false,
        gearHistoryModal: {
            show: false,
            gearHistory: [],
            gearReservationHistory: []
        }
    };
}

// create actions and export them for use
export const GearActions = Reflux.createActions([
    "tabSelected",
    "updateDropdown",
    "fetchGearList",
    "openGearModal",
    "gearModalChanged",
    "submitGearModal",
    "closeGearModal",
    "gearModalTabSelected",
    "fetchGearCategoryList",
    "openCategoryModal",
    "categoryModalChanged",
    "submitCategoryModal",
    "closeCategoryModal",
    "addToShoppingCart",
    "removeFromShoppingCart",
    "closeCategoryModal",
    "submitDeleteGearModal",
    "openDeleteGearModal",
    "closeDeleteGearModal",
    "submitDeleteGearCategoryModal",
    "openDeleteGearCategoryModal",
    "closeDeleteGearCategoryModal",
    "removeFromShoppingCart",
    "openReserveGearForm",
    "reserveGearFormChanged",
    "submitReserveGearForm",
    "closeReserveGearForm",
    "fileSelected",
    "uploadGearFile",
    "getGearFile",
    "gearStatusCheckBoxChange",
    "dateFilterChanged",
    "fetchGearListFromTo",
    "fetchRentableListFromTo",
    "updateConditionDropdown",
    "fetchRentableGearList",
    "openGearHistoryModal",
    "closeGearHistoryModal"
]);

export class GearStore extends Reflux.Store {
    constructor() {
        super();
        this.state = defaultState();
        this.listenables = GearActions; // listen for actions
    }

    onTabSelected(tab) {
        this.setState({
            tabSelected: tab
        });
    }

    // updates the selected object in the category dropdown
    onUpdateDropdown(value) {
        this.setState({
            categoryDropdown: { categorySelected: value }
        });
    }

    onUpdateConditionDropdown(value) {
        this.setState({
            conditionSelected: value
        });
    }

    onFetchGearList() {
        const service = new GearService();

        this.setState({
            fetchedGearList: true
        });

        return service.fetchGearList()
            .then(({ data, error }) => {
                if (data) {
                    this.setState({
                        gearList: data
                    });
                } else {
                    this.setState({
                        error: true,
                        errorMessage: error
                    });
                }
            });
    }

    onFetchRentableGearList() {
        const service = new GearService();

        this.setState({
            fetchedRentableGearList: true
        });

        return service.fetchGearList()
            .then(({ data, error }) => {
                if (data) {
                    this.setState({
                        rentableList: data.filter(
                            (gear) => {
                                return gear.condition === "RENTABLE";
                            }
                        )
                    });
                } else {
                    this.setState({
                        error: true,
                        errorMessage: error
                    });
                }
            });
    }

    onGearModalTabSelected(tab) {
        this.setState(update(this.state, {
            gearModal: {
                tabSelected: { $set: tab }
            }
        }));
    }

    // opens the gear modal, mode is to specify if the modal is for creating or editing gear
    onOpenGearModal(mode = Constants.modals.CREATING, options = { gear: {} }) {
        if (Object.keys(options.gear).length !== 0 && options.gear.constructor === Object) {
            this.fetchGearHistory(options.gear);
        }
        const { id, expectedVersion, gearCode, depositFee, gearCategory, gearDescription, gearCondition, gearStatus } = options.gear,
            newState = update(this.state, {
                gearModal: {
                    show: { $set: true },
                    mode: { $set: mode },
                    id: { $set: id || null },
                    expectedVersion: { $set: expectedVersion || null },
                    gearCode: { $set: gearCode || "" },
                    depositFee: { $set: depositFee || "" },
                    gearCategory: { $set: gearCategory || "" },
                    gearDescription: { $set: gearDescription || "" },
                    gearCondition: { $set: gearCondition || "" },
                    gearStatus: { $set: gearStatus || "" }
                }
            });
        this.setState(newState);
    }

    // updates the field values of the gearModal
    onGearModalChanged(field, value) {
        const newState = update(this.state, {
            gearModal: {
                [field]: { $set: value }
            }
        });
        this.setState(newState);
    }

    // sets an error for the gearModal (i.e. no internet, etc)
    onSetGearModalError(message) {
        const newState = update(this.state, {
            gearModal: {
                error: { $set: true },
                errorMessage: { $set: message }
            }
        });
        this.setState(newState);
    }

    // tries to submit the data in the gearModal for creating/editing gear
    onSubmitGearModal() {
        const service = new GearService();

        if (this.state.gearModal.gearCategory === "") {
            this.onSetGearModalError("You need to select a category.");
            return;
        }

        if (this.state.gearModal.mode === Constants.modals.CREATING) {
            // creating a new piece of gear
            return service.createGear({ ...this.state.gearModal })
                .then(({ gear, error }) => {
                    if (gear) {
                        const newState = update(this.state, {
                            gearList: { $push: [gear] }
                        });
                        this.setState(newState);
                        this.onCloseGearModal();
                    } else {
                        this.onSetGearModalError(error);
                    }
                });
        } else {
            // else: Not creating a new piece of gear
            return service.updateGear({ ...this.state.gearModal })
                .then(({ gear, error }) => {
                    if (gear) {
                        const indexToUpdate = this.state.gearList.findIndex((obj) => obj.id === gear.id),
                            newState = update(this.state, {
                                gearList: {
                                    [indexToUpdate]: { $set: gear }
                                }
                            });

                        this.setState(newState);
                        this.onCloseGearModal();
                    } else {
                        this.onSetGearModalError(error);
                    }
                });
        }
    }

    // closes and returns the gear modal back to its default/closed values
    onCloseGearModal() {
        const newState = update(this.state, {
            gearModal: { $set: defaultState().gearModal }
        });
        this.setState(newState);
    }

    // gets the gear category list from the back-end and sets it in the state
    onFetchGearCategoryList() {
        const service = new GearService();

        // helps prevent calling this function too many times
        this.setState({ fetchedGearCategoryList: true });

        return service.fetchGearCategoryList()
            .then(({ data, error }) => {
                if (data) {
                    this.setState({
                        categoryList: data.sort(gearCategorycompare)
                    });
                } else if (error) {
                    this.setState({
                        error: true,
                        errorMessage: error
                    });
                }
            });
    }

    onOpenCategoryModal(mode = Constants.modals.CREATING, options = { category: {} }) {
        const { name } = options.category,
            newState = update(this.state, {
                categoryModal: {
                    show: { $set: true },
                    mode: { $set: mode },
                    originalName: { $set: name || null },
                    category: { $set: name || "" }
                }
            });
        this.setState(newState);
    }

    categoryModalChanged(field, value) {
        const newState = update(this.state, {
            categoryModal: {
                [field]: { $set: value }
            }
        });
        this.setState(newState);
    }

    onSetCategoryModalError(message) {
        const newState = update(this.state, {
            categoryModal: {
                error: { $set: true },
                errorMessage: { $set: message }
            }
        });
        this.setState(newState);
    }

    onSubmitCategoryModal() {
        const service = new GearService();

        if (this.state.categoryModal.category === "") {
            this.onSetCategoryModalError("You cannot leave the category name blank.");
            return;
        }

        if (this.state.categoryModal.mode === Constants.modals.CREATING) {
            // creating a new piece of gear
            return service.createCategory({ name: this.state.categoryModal.category })
                .then(({ category, error }) => {
                    if (category) {
                        const newState = update(this.state, {
                            categoryList: { $push: [category] }
                        });
                        this.setState(newState);
                        this.onCloseCategoryModal();
                    } else {
                        this.onSetCategoryModalError(error);
                    }
                });
        } else {
            // else: Not creating a category
            const { categoryModal: { originalName, category } } = this.state; // destructuring
            return service.updateCategory({ originalName, newName: category })
                .then(({ category, error }) => {
                    const { categoryList, categoryModal: { originalName } } = this.state; // destructuring

                    if (category) {
                        const indexToUpdate = categoryList.findIndex((obj) => obj.name === originalName),
                            newState = update(this.state, {
                                categoryList: {
                                    [indexToUpdate]: { $set: category }
                                }
                            });

                        this.setState(newState);
                        this.onCloseCategoryModal();
                        return this.onFetchGearList(); // easier to call this than update all the gear data
                    } else {
                        this.onSetCategoryModalError(error);
                    }
                });
        }
    }

    onCloseCategoryModal() {
        const newState = update(this.state, {
            categoryModal: { $set: defaultState().categoryModal }
        });
        this.setState(newState);
    }

    onAddToShoppingCart(row) {
        let isNewItem = false;
        this.state.shoppingList.forEach(function(gear) {
            if (gear.id === row.id) {
                isNewItem = true;
            }
        });
        if (!isNewItem) {
            const newState = update(this.state, {
                shoppingList: { $push: [row] },
                checkoutDisabled: { $set: false },
                rentableList: {
                    $set: this.state.rentableList.filter(
                        (gear) => {
                            return gear.id !== row.id;
                        }
                    )
                }
            });
            this.setState(newState);
        } else {
            toast.error(`Gear ID: ${row.code} is already in your shopping cart`);
        }
    }

    onRemoveFromShoppingCart(row) {
        let newCheckoutDisabledValue = false;
        if (this.state.shoppingList.length <= 1) {
            newCheckoutDisabledValue = true;
        }
        const newState = update(this.state, {
            shoppingList: {
                $set: this.state.shoppingList.filter((obj) =>
                    row.id !== obj.id)
            },
            checkoutDisabled: { $set: newCheckoutDisabledValue },
            rentableList: { $push: [row] }
        });
        this.setState(newState);
    }

    onOpenDeleteGearModal(id) {
        const newState = update(this.state, {
            deleteGearModal: {
                id: { $set: id },
                show: { $set: true },
                error: { $set: false },
                errorMessage: { $set: "" }
            }
        });
        this.setState(newState);
    }

    onSubmitDeleteGearModal() {
        const service = new GearService();
        return service.deleteGear(this.state.deleteGearModal.id)
            .then(({ error }) => {
                if (error) {
                    const newState = update(this.state, {
                        deleteGearModal: {
                            error: { $set: true },
                            errorMessage: { $set: error }
                        }
                    });
                    this.setState(newState);
                } else {
                    for (let i = 0; i < this.state.gearList.length; i++) {
                        if (this.state.gearList[i].id === this.state.deleteGearModal.id) {
                            const newState = update(this.state, {
                                gearList: {
                                    [i]: {
                                        condition: { $set: "DELETED" }
                                    }
                                }
                            });
                            this.setState(newState);
                            break;
                        }
                    }
                    this.onCloseDeleteGearModal();
                }
            });
    }

    onCloseDeleteGearModal() {
        const newState = update(this.state, {
            deleteGearModal: { $set: defaultState().deleteGearModal }
        });
        this.setState(newState);
    }

    // opens the delete gear category modal
    onOpenDeleteGearCategoryModal(name) {
        const newState = update(this.state, {
            deleteGearCategoryModal: {
                name: { $set: name },
                show: { $set: true },
                error: { $set: false },
                errorMessage: { $set: "" }
            }
        });
        this.setState(newState);
    }

    onSubmitDeleteGearCategoryModal() {
        const service = new GearService();
        return service.deleteCategory(this.state.deleteGearCategoryModal.name)
            .then(({ error }) => {
                if (error) {
                    const newState = update(this.state, {
                        deleteGearCategoryModal: {
                            error: { $set: true },
                            errorMessage: { $set: error }
                        }
                    });
                    this.setState(newState);
                } else {
                    const newState = update(this.state, {
                        categoryList: {
                            $set: this.state.categoryList.filter(
                                (obj) => {
                                    return obj.name !== this.state.deleteGearCategoryModal.name;
                                }
                            )
                        }
                    });
                    this.setState(newState);
                    this.onCloseDeleteGearCategoryModal();
                }
            });
    }

    onCloseDeleteGearCategoryModal() {
        const newState = update(this.state, {
            deleteGearCategoryModal: { $set: defaultState().deleteGearCategoryModal }
        });
        this.setState(newState);
    }

    onOpenReserveGearForm() {
        if (this.state.shoppingList.length > 0) {
            const newState = update(this.state, {
                reserveGearForm: {
                    show: { $set: true },
                    error: { $set: false }
                }
            });
            this.setState(newState);
        }
    }

    onReserveGearFormChanged(field, value) {
        const newState = update(this.state, {
            reserveGearForm: {
                [field]: { $set: value }
            }
        });
        this.setState(newState);
    }

    onSubmitReserveGearForm() {
        const gearIdList = [], service = new GearService(),
            newState = update(this.state, {
                reserveGearForm: {
                    items: { $set: gearIdList }
                }
            });
        this.state.shoppingList.forEach(function(gear) {
            gearIdList.push(gear.id);
        });
        this.setState(newState);
        return service.submitReservation(this.state.reserveGearForm)
            .then(({ error }) => {
                if (error) {
                    const newState = update(this.state, {
                        reserveGearForm: {
                            error: { $set: true },
                            errorMessage: { $set: error }
                        }
                    });
                    this.setState(newState);
                } else {
                    const newState = update(this.state, {
                        shoppingList: { $set: defaultState().shoppingList },
                        checkoutDisabled: { $set: defaultState().checkoutDisabled }
                    });
                    this.setState(newState);
                    this.onCloseReserveGearForm();
                    toast("Reservation Success");
                }
            });
    }

    onCloseReserveGearForm() {
        const newState = update(this.state, {
            reserveGearForm: {
                show: { $set: false },
                error: { $set: false }
            }
        });
        this.setState(newState);
    }

    onFileSelected(file) {
        const service = new GearService(),
            newState = update(this.state, {
                upload: { $set: defaultState().upload }
            });

        this.setState(newState); // prevent accidentally propagating old info

        if (file) {
            return service.parseGearFile(file)
                .then(({ gear, categories, warnings }) => {
                    const newState = update(this.state, {
                        upload: {
                            gear: { $set: gear },
                            categories: { $set: categories },
                            warnings: { $set: warnings }
                        }
                    });
                    this.setState(newState);
                })
                .catch((error) => {
                    const newState = update(this.state, {
                        upload: {
                            error: { $set: error.toString() }
                        }
                    });
                    this.setState(newState);
                });
        }
    }

    onUploadGearFile() {
        const { gear, categories } = this.state.upload,
            service = new GearService();

        return service.uploadGearFile(categories, gear)
            .then(({ failed }) => {
                const newState = update(this.state, {
                    upload: {
                        results: {
                            show: { $set: true },
                            failed: { $set: failed }
                        }
                    }
                });
                this.setState(newState);
                GearActions.fetchGearList();
                GearActions.fetchGearCategoryList();
            });
    }

    onGetGearFile() {
        const service = new GearService();
        service.createGearFile(this.state.gearList);
    }

    onGearStatusCheckBoxChange(checkboxKey, checkBoxChecked) {
        const newState = update(this.state, {
            checkboxOptions: {
                [checkboxKey]: { $set: checkBoxChecked }
            }
        });
        this.setState(newState);
    }

    onDateFilterChanged(field, date) {
        const newState = update(this.state, {
            reserveGearForm: {
                [field]: { $set: new Date(date) }
            }
        });
        this.setState(newState);
    }

    onFetchRentableListFromTo(startDate, endDate) {
        const service = new GearService(),
            startDateString = moment(startDate).format("YYYY-MM-DD"),
            endDateString = moment(endDate).format("YYYY-MM-DD");
        return service.fetchGearListFromTo(startDateString, endDateString)
            .then(({ data }) => {
                const shoppingCartRemove = {}, rentalListRemove = {};
                if (data) {
                    this.state.shoppingList.forEach(function(gear) {
                        const found = data.find(function(element) {
                            return element.id === gear.id;
                        });
                        if (!found) {
                            shoppingCartRemove[gear.id] = true;
                        } else {
                            rentalListRemove[gear.id] = true;
                        }
                    });
                    if (Object.keys(shoppingCartRemove).length) {
                        toast.error("Some items have been removed from your shopping cart because it is  unavailable in the selected date range.");
                    }
                    this.setState({
                        rentableList: data.filter(
                            (gear) => !rentalListRemove[gear.id]
                        ),
                        shoppingList: this.state.shoppingList.filter(
                            (gear) => !shoppingCartRemove[gear.id]
                        )
                    });
                }
            });
    }

    fetchGearHistory(gear) {
        if (gear) {
            const gearService = new GearService(),
                reservationService = new ReservationService(),
                gearHistoryPromise = gearService.fetchGearHistory(gear.id)
                    .then(({ data, error }) => {
                        if (data) {
                            return data;
                        } else {
                            return error;
                        }
                    }),
                gearReservationHistoryPromise =
                    reservationService.fetchGearReservationHistory(gear.id)
                        .then(({ data, error }) => {
                            if (data) {
                                return data;
                            } else {
                                return error;
                            }
                        });

            return Promise.all([gearHistoryPromise, gearReservationHistoryPromise])
                .then((values) => {
                    const gearHistory = values[0],
                        gearReservationHistory = values[1];

                    // It does not matter if the value is real or an error
                    // Set it as the history
                    this.setState(update(this.state, {
                        gearModal: {
                            gearHistory: { $set: gearHistory },
                            gearReservationHistory: { $set: gearReservationHistory }
                        }
                    }));
                });
        }
    }
}
