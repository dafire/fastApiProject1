// noinspection ES6UnusedImports

import './scss/styles.scss'

import * as Turbo from "@hotwired/turbo"

import {Application} from "@hotwired/stimulus"
import {definitionsFromContext} from "@hotwired/stimulus-webpack-helpers"

window.Stimulus = Application.start()
const context = require.context("./controllers", true, /\.js$/)
Stimulus.load(definitionsFromContext(context))