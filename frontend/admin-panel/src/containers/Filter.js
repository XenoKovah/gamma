import React from 'react';

import 'date-fns';

import InputNumber from 'rc-input-number';
import Select from 'react-select';

import { MuiPickersUtilsProvider, DatePicker } from 'material-ui-pickers';
import DateFnsUtils from '@date-io/date-fns';

import {AllowedFilters, isObjectEmpty, getOrgFromCourseKey } from '../Utils';

import { COURSES, ORGANISATIONS } from '../api/Api';
import { customStyles } from '../components/Select';

import "react-datepicker/dist/react-datepicker.css";


export default class Filter extends React.Component {
    constructor(props) {
        super(props);

        this.customFilterStyles = {
            option: (provided, state) => ({
                ...provided,
                textTransform: 'none !important'
            })
        };

        this.handleChangeDateStart = this.handleChangeDateStart.bind(this);
        this.handleChangeDateEnd = this.handleChangeDateEnd.bind(this);
        this.handleChangeInput = this.handleChangeInput.bind(this);
        this.clearStart = this.clearStart.bind(this);
        this.clearEnd = this.clearEnd.bind(this);
        this.getEmptyFields = this.getEmptyFields.bind(this);
        this.addField = this.addField.bind(this);
        this.handleBlurInput = this.handleBlurInput.bind(this);
        this.avFieldsChanged = this.avFieldsChanged.bind(this);
        this.handleFocus = this.handleFocus.bind(this);
        this.getOrganisations = this.getOrganisations.bind(this);
        this.getCurrentCourses = this.getCurrentCourses.bind(this);
        this.getCurrentOrganisations = this.getCurrentOrganisations.bind(this);
    }

    state = {
        org: this.props.org || "",
        interval: this.props.interval || {},
        frequency: this.props.frequency || 0,
        course: this.props.course || "",
        courses: [],
        organisations: [],
        manuallyAdded: {
            org: false,
            interval: false,
            frequency: false,
            course: false
        },
        filter: {
            selectedItem: null
        }
    }

    getCourses() {
        fetch(process.env.REACT_APP_LOCALHOST + COURSES)
        .then(resp => resp.json())
        .then(result => {
            this.setState({
                courses: result.courses
            })
        })
    }

    componentDidMount() {
        this.getCourses();
        this.getOrganisations();
    }

    handleFocus() {
        this.setState({...this.props})
    }

    avFieldsChanged(item, meta) {
        this.setState({
            filter: {
                selectedItem: item
            }
        });
    }

    addField() {
        const {
            filter: { selectedItem },
            manuallyAdded
        } = this.state;

        if (selectedItem) {
            if (selectedItem.value == 'frequency') {
                this.setState({frequency: 1});
                this.props.onChange('frequency', 1);
            }

            manuallyAdded[selectedItem.value] = true;

            this.setState({
                manuallyAdded: manuallyAdded,
                filter: {
                    selectedItem: null
                }
            });
        }
    }

    getEmptyFields() {
        let emptyFields = AllowedFilters.filter((field) => {
            return (field === 'interval' && isObjectEmpty(this.state[field]) && !this.state.manuallyAdded[field]) || (!this.state[field] && !this.state.manuallyAdded[field]);
        });
        return emptyFields;
    }

    clearEnd(event) {
        let state = this.state;
        delete state.interval['end'];
        if (!state.interval.start) {state.manuallyAdded.interval = false;}
        this.setState(state, () => {
            this.props.onChange("end", null);
        })
    }

    clearStart(event) {
        let state = this.state;
        delete state.interval['start'];
        if (!state.interval.end) {state.manuallyAdded.interval = false;}
        this.setState(state, () => {
            this.props.onChange("start", null);
        })
    }

    handleChangeDate(date, type) {
        let state = this.state;
        state.interval[type] = date;
        state.stateUpdated = false;

        this.setState(state, () => {
            if (!state.interval[type] && !date) {
                state.manuallyAdded.interval = false;
                delete state.interval;
                this.setState(state);
                this.props.onChange("interval", {});
            } else {
                this.props.onChange(type, date);
            }
        });
    }

    handleChangeDateEnd(date) {
        this.handleChangeDate(date, "end");
    }

    handleChangeDateStart(date) {
        this.handleChangeDate(date, "start");
    }

    getOrganisations() {
        fetch(process.env.REACT_APP_LOCALHOST + ORGANISATIONS)
        .then(resp => resp.json())
        .then(result => {
            this.setState({
                organisations: result.organisations
            })
        })
    }

    getCurrentCourses(org='', courses, emptySelectValue) {
        if (org && courses) {
            // Select only those courses belonging to the selected organization
            courses = courses.filter(
                (course) => getOrgFromCourseKey(course) === org
            )
        }
        courses = emptySelectValue.concat(
            courses.map(el => {
                return {value: el, label: el}
            })
        );
        return courses
    }

    getCurrentOrganisations(course='', organisations, emptySelectValue) {
        if (course && organisations) {
            // Show only those org related to the selected course
            const courseOrg = getOrgFromCourseKey(course);
            organisations = emptySelectValue.concat(
                {value: courseOrg, label: courseOrg}
            )
        } else {
            // Show all organisations
            organisations = emptySelectValue.concat(
                organisations.map(el => {
                    return {value: el, label: el}
                })
            );
        }
        return organisations
    }

    handleChangeInput (event, meta) {
        let state = this.state;
        let name, value;
        if (meta) {
            name = meta.name;
            value = event.value
        } else {
            name = 'frequency';
            value = event
        }
        state[name] = value;
        state.manuallyAdded[name] = value ? false : true;
        this.props.onChange(name, value);
        this.setState(state);
    }

    handleBlurInput(event) {
        let name = event.target.name;
        let value = event.target.value;
        if (!name) {
            name = event.target.id;
            value = this.state[name];
        }
        let {manuallyAdded} = this.state;
        if(!value) {
            manuallyAdded[name] = false;
        }
        this.setState({
            manuallyAdded: manuallyAdded,
            name: value,
            stateUpdated: false
        }, () => {this.props.onChange(name, value)})
    }

    shouldComponentUpdate(nextProps, nextState) {
        if (nextProps.shouldFilterUpdate && !this.state.stateUpdated){
            this.setState({
                stateUpdated: true,
                ...nextProps
            })
        }
        return true;
    }

    render() {
        const { filter: { selectedItem: filterSelectedItem } } = this.state;
        const { org, course, interval } = this.state;
        let { courses, organisations } = this.state;
        const start = interval && interval.start ? interval.start : null;
        const end = interval && interval.end ? interval.end : null;
        let emptySelectValue = [{value: null, label: "------"}];

        courses = this.getCurrentCourses(org, courses, emptySelectValue);
        organisations = this.getCurrentOrganisations(course, organisations, emptySelectValue);

        let emptyFields = this.getEmptyFields().map(el => {
            return {value: el, label: el};
        });
        let currentCourse = {value: this.state.course, label: this.state.course};
        let currentOrg = {value: this.state.org, label:this.state.org};
        return (
            <div>
                <h3>{gettext('Filters')}</h3>
                <div className="FilterItem" data-testid="FilterItem">
                    {
                        this.state.course || this.state.manuallyAdded.course ? (
                            <div className="FormGroup">
                                <label htmlFor="courses">{gettext('Courses')}</label>
                                <Select inputId="course" name="course"
                                    styles={customStyles}
                                    value={currentCourse}
                                    onChange={this.handleChangeInput}
                                    onBlur={this.handleBlurInput}
                                    className="Select Select--filter"
                                    classNamePrefix="react-select"
                                    options={courses}
                                    placeholder="-----"/>
                            </div>
                        ) : false
                    }
                    {
                        this.state.org || this.state.manuallyAdded.org ? (
                            <div className="FormGroup">
                                <label htmlFor="org">{gettext('Organisation')}</label>
                                <Select inputId="org" name="org"
                                    styles={this.customFilterStyles}
                                    value={currentOrg}
                                    onChange={this.handleChangeInput}
                                    onBlur={this.handleBlurInput}
                                    className="Select"
                                    placeholder="-----"
                                    options={organisations}/>
                            </div>
                        ) : false
                    }

                    {
                        this.state.frequency || this.state.manuallyAdded.frequency ? (
                            <div className="FormGroup">
                                <label htmlFor="frequency">{gettext('Frequency')}</label>
                                <InputNumber name="frequency" id="frequency" type="number" min={0}
                                    value={this.state.frequency}
                                    onChange={this.handleChangeInput}
                                    onBlur={this.handleBlurInput}
                                    // onFocus={this.handleFocus}
                                    />
                            </div>
                        ) : false
                    }
                    {
                        !isObjectEmpty(this.state.interval) || this.state.manuallyAdded.interval ? (
                            <div>
                                <div className="FormGroup isDatePicker">

                                    <MuiPickersUtilsProvider utils={DateFnsUtils}>
                                        <DatePicker
                                            margin="normal"
                                            label="Start interval"
                                            value={start}
                                            maxDate={end || undefined}
                                            maxDateMessage={gettext("End interval should be greater then Start interval")}
                                            onChange={this.handleChangeDateStart}
                                            className="DatePicker-Group"
                                        />

                                    </MuiPickersUtilsProvider>
                                    <button className="Btn Btn_danger" onClick={this.clearStart}>{gettext('Clear')}</button>
                                </div>
                                <div className="FormGroup isDatePicker">

                                    <MuiPickersUtilsProvider utils={DateFnsUtils}>
                                        <DatePicker
                                            margin="normal"
                                            label="End interval"
                                            value={end}
                                            minDate={start || undefined}
                                            minDateMessage={gettext("Start interval should be less then End interval")}
                                            onChange={this.handleChangeDateEnd}
                                            className="DatePicker-Group"
                                        />

                                    </MuiPickersUtilsProvider>
                                    <button className="Btn Btn_danger" onClick={this.clearEnd}>{gettext('Clear')}</button>
                                </div>
                            </div>
                        ) : false
                    }
                    <div className="Action">

                        {
                            emptyFields.length ? (
                                <div className="FormGroup">
                                    <label htmlFor="avFields">{gettext('Add fields')}</label>
                                    <Select id="avFields"
                                            onChange={this.avFieldsChanged}
                                            className="Select"
                                            defaultInputValue=""
                                            value={filterSelectedItem}
                                            styles={customStyles}
                                            options={emptyFields}/>
                                    <button className="Btn Btn_primary Btn_add" onClick={this.addField}>{gettext('Add')}</button>
                                </div>
                            ) : false
                        }

                    </div>
                </div>

            </div>
        )
    }
}

// Filter.propTypes = {
//     org: PropTypes.string
// }
