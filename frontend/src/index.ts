import './scss/styles.scss'


import * as Turbo from "@hotwired/turbo"
import {Application} from "@hotwired/stimulus"
import {definitionsFromContext} from "@hotwired/stimulus-webpack-helpers"


let Stimulus = Application.start()
const context = require.context("./controllers", true, /\.ts$/)
Stimulus.load(definitionsFromContext(context))
Turbo.start()
