import { create } from 'ipfs-http-client'
import { dummyLogger, Logger } from "ts-log";


export class IpfsService {
    ipfsHost = process.env.ipfs_host || ''
    ipfsClient = create({
        host: this.ipfsHost
    })

    async store(data: any) {
        console.log(data)
        try {
            const resp = await this.ipfsClient.add(data);
            dummyLogger.info(`Data stored in IPFS. CID: ${resp.cid}`);
            return resp;
        } catch (e) {
            dummyLogger.error(e);
        }
    }
}