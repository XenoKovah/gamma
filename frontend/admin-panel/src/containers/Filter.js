import React from 'react';

import PropTypes from 'prop-types';
import 'date-fns';

import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';
import TextField from '@material-ui/core/TextField';
import { Divider } from '@material-ui/core';
import Button from '@material-ui/core/Button';

import FormGroup from '@material-ui/core/FormGroup';
import InputBase from '@material-ui/core/InputBase';

import { MuiPickersUtilsProvider, TimePicker, DatePicker } from 'material-ui-pickers';
import Grid from '@material-ui/core/Grid';
import DateFnsUtils from '@date-io/date-fns';
import Select from '@material-ui/core/Select';

import "react-datepicker/dist/react-datepicker.css";


export default class Filter extends React.Component {
    constructor(props) {
        super(props);

        this.handleChangeDateStart = this.handleChangeDateStart.bind(this);
        this.handleChangeDateEnd = this.handleChangeDateEnd.bind(this);
        this.handleChangeInput = this.handleChangeInput.bind(this);
        this.clearStart = this.clearStart.bind(this);
        this.clearEnd = this.clearEnd.bind(this);
        
    }

    clearEnd(event) {
        this.setState({
            end: null
        }, () => {
            this.props.onChange("end", null);
        })
    }

    clearStart(event) {
        this.setState({
            start: null
        }, () => {
            this.props.onChange("start", null);
        })
    }

    handleChangeDateStart(date) {
        let formattedDate = date.toISOString();
        this.setState({
            start: formattedDate
        }, () => {
            this.props.onChange("start", formattedDate);
        })
    }

    handleChangeDateEnd(date) {
        let formattedDate = date.toISOString();
        this.setState({
            end: formattedDate
        }, () => {
            this.props.onChange("end", formattedDate);
        })
    }

    handleChangeInput (event) {
        let state = {};
        let name = event.currentTarget.name;
        let value = event.currentTarget.value;
        state[name] = value;
        this.setState(state, () => {
            this.props.onChange(name, value);
        });
    }

    render() {
        let start = this.props && this.props.interval && this.props.interval.start ? this.props.interval.start : null;
        let end = this.props && this.props.interval && this.props.interval.end ? this.props.interval.end : null;
        return (
            <div>
                <h3>Filters</h3>
                <FormGroup>
                    <InputLabel htmlFor="org">Org</InputLabel>
                    <Input name="org" id="org"
                        value={this.props.org}
                        onChange={this.handleChangeInput}/>

                    <InputLabel htmlFor="frequency">Frequency</InputLabel>
                    <Input name="frequency" id="frequency" type="number"
                        value={this.props.frequency}
                        onChange={this.handleChangeInput}
                        />
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
                {/* <div className="Action">

                    {
                        this.getAvailableFields().length ? (
                            <div>
                                <FormGroup>
                                    <InputLabel htmlFor="avFields">Available filter fields</InputLabel>
                                    <Select id="avFields" native ref={s => {this.selectedField = s && s.props.children[0].props.value}} onChange={this.avFieldsChanged}>
                                        {
                                            this.getAvailableFields().map((el, ind) => {
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

                </div> */}
                {/* <div className="Action">
                    <Button size="small" onClick={this.removeFilter} variant="contained" color="secondary">Remove filter</Button>
                </div> */}
                </FormGroup>

            </div>
        )
    }
}

// Filter.propTypes = {
//     org: PropTypes.string
// }
