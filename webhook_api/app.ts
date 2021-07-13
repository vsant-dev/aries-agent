import express from 'express'

import agentRouter from './lib/web/router/agent'

const app = express();

app.use(express.json());
app.use(agentRouter);

app.listen(3200);

