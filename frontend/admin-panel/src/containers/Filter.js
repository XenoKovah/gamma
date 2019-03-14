import React from 'react';

import PropTypes from 'prop-types';
import 'date-fns';

import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';
import Select from '@material-ui/core/Select';
import { Divider } from '@material-ui/core';
import Button from '@material-ui/core/Button';

import FormGroup from '@material-ui/core/FormGroup';
import InputBase from '@material-ui/core/InputBase';

import { MuiPickersUtilsProvider, TimePicker, DatePicker } from 'material-ui-pickers';
import Grid from '@material-ui/core/Grid';
import DateFnsUtils from '@date-io/date-fns';

import {AllowedFilters, isObjectEmpty} from '../Utils';

import "react-datepicker/dist/react-datepicker.css";

var changed = false;

export default class Filter extends React.Component {
    constructor(props) {
        super(props);

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
        
    }

    state = {
        org: this.props.org || "",
        interval: this.props.interval || {},
        frequency: this.props.frequency || 0,
        manuallyAdded: {
            org: false,
            interval: false,
            frequency: false
        }
    }

    handleFocus() {
        this.setState({...this.props})
    }

    avFieldsChanged(event) {
        this.selectedField = event.target.value;
    }

    addField() {
        let manuallyAdded = this.state.manuallyAdded;
        manuallyAdded[this.selectedField] = true;
        this.setState({
            manuallyAdded: manuallyAdded
        })
    }

    getEmptyFields() {

        let emptyFields = AllowedFilters.filter((field) => {
            return field == 'interval' && isObjectEmpty(this.props[field]) || !this.props[field];
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

    handleChangeDateStart(date) {
        let formattedDate = date.toISOString();
        this.setState({
            start: formattedDate
        }, () => {
            let state = this.state;
            if (!state.interval.start && !state.interval.end) {
                state.manuallyAdded.interval = false;
                delete state['interval'];
                this.setState(state);
                this.props.onChange("interval", {});
            } else {
                this.props.onChange("start", formattedDate);
            }
        })
    }

    checkInterval() {

    }

    handleChangeDateEnd(date) {
        let formattedDate = date.toISOString();
        this.setState({
            end: formattedDate
        }, () => {
            let state = this.state;
            if (!this.state.interval.start && !this.state.interval.end) {
                state.manuallyAdded.interval = false;
                delete state['interval'];
                this.setState(state);
                this.props.onChange("interval", {});
            } else {
                this.props.onChange("end", formattedDate);
            }
        })
    }

    handleChangeInput (event) {
        let state = {};
        let name = event.currentTarget.name;
        let value = event.currentTarget.value;
        state[name] = value;
        this.setState(state);
    }

    handleBlurInput(event) {
        this.props.onChange(event.target.name, event.target.value);
    }

    static getDerivedStateFromProps(nextProps, prevState) {
        if (!nextProps.org == prevState.org && !changed) {
            changed = true;
            return {
                org: nextProps.org,
                interval: nextProps.interval,
                frequency: nextProps.frequency
            };
        }
        return null;
      }

    render() {
        let start = this.state && this.state.interval && this.state.interval.start ? this.state.interval.start : null;
        let end = this.state && this.state.interval && this.state.interval.end ? this.state.interval.end : null;
        return (
            <div>
                <h3>Filters</h3>
                <FormGroup>
                    {
                        this.props.org || this.state.manuallyAdded.org ? (
                            <div>
                                <InputLabel htmlFor="org">Org</InputLabel>
                                <Input name="org" id="org"
                                    value={this.state.org}
                                    onChange={this.handleChangeInput}
                                    onBlur={this.handleBlurInput}/>
                            </div>
                        ) : false
                    }

                    {
                        this.props.frequency || this.state.manuallyAdded.frequency ? (
                            <div>
                                <InputLabel htmlFor="frequency">Frequency</InputLabel>
                                <Input name="frequency" id="frequency" type="number"
                                    value={this.state.frequency}
                                    onChange={this.handleChangeInput}
                                    onBlur={this.handleBlurInput}
                                    onFocus={this.handleFocus}
                                    />
                            </div>
                        ) : false
                    }
                    {
                        !isObjectEmpty(this.props.interval) || this.state.manuallyAdded.interval ? (
                            <div>
                                <div className="DatePickerBlock">

                                    <MuiPickersUtilsProvider utils={DateFnsUtils}>
                                        <Grid container justify="space-around">
                                        <DatePicker
                                            margin="normal"
                                            label="Start interval"
                                            value={start}
                                            onChange={this.handleChangeDateStart}
                                        />
                                        
                                        </Grid>
                                    </MuiPickersUtilsProvider>
                                    <Button size="small" mini={true} onClick={this.clearStart} variant="contained" color="secondary">Clear</Button>
                                    </div>
                                    <div className="DatePickerBlock">

                                    <MuiPickersUtilsProvider utils={DateFnsUtils}>
                                        <Grid container justify="space-around">
                                        <DatePicker
                                            margin="normal"
                                            label="End interval"
                                            value={end}
                                            onChange={this.handleChangeDateEnd}
                                        />
                                        
                                        </Grid>
                                        <Button size="small" mini={true} onClick={this.clearEnd} variant="contained" color="secondary">Clear</Button>
                                    </MuiPickersUtilsProvider>
                                </div>
                            </div>
                        ) : false
                    }
                <div className="Action">

                    {
                        this.getEmptyFields().length ? (
                            <div>
                                <FormGroup>
                                    <InputLabel htmlFor="avFields">Add fields</InputLabel>
                                    <Select id="avFields" native ref={s => {this.selectedField = s && s.props.children[0].props.value}} onChange={this.avFieldsChanged}>
                                        {
                                            this.getEmptyFields().map((el, ind) => {
                                                return <option key={ind+1} value={el}>{el}</option>
                                            })
                                        }
                                    </Select>
                                    <div className="Action">
                                        <Button size="small" variant="contained" color="primary" onClick={this.addField}>Add field</Button>
                                    </div>
                                </FormGroup>
                            </div>
                        ) : false
                    }

                </div>
                </FormGroup>

            </div>
        )
    }
}

// Filter.propTypes = {
//     org: PropTypes.string
// }
